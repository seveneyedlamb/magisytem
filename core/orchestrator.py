import json
from llm.client import make_api_call
from llm.messages import append_user, append_assistant, append_tool
from core.personalities import MELCHIOR_PROMPT, BALTHASAR_PROMPT, CASPER_PROMPT
from core.addressing import get_addressed_personalities
from tools.schema import TOOL_SCHEMAS
from core.config import CONFIG

# MAGI Core — the overseer/briefer. Not a personality. A neutral reformulator.
MAGI_CORE_SYSTEM = (
    "You are MAGI CORE, the administrative overseer of the MAGI deliberation system. "
    "Your job: receive the user's raw query and rewrite it as a clear structured briefing "
    "for the council of three (CASPER, BALTHASAR, MELCHIOR). "
    "Format your briefing as:\n"
    "OBJECTIVE: [what they want — one sentence]\n"
    "CONTEXT: [relevant context, constraints, what we know]\n"
    "GUIDANCE: [tone, style, or specific instructions — e.g. 'Dave Barry humor', 'no em dashes']\n\n"
    "Be precise. Be brief. Max 120 words total. Do not answer the question yourself."
)

# MAGI clipboard evaluator — decides if an item is worth keeping in session memory
MAGI_CLIPBOARD_SYSTEM = (
    "You are MAGI CORE evaluating whether a piece of information deserves to be added "
    "to the session clipboard — a shared context list visible to all agents in future queries. "
    "Clipboard items should be: factual, specific, reusable, non-obvious. "
    "NOT worth adding: summaries of what was just said, vague statements, opinions without facts. "
    "Respond with exactly one of:\n"
    "APPROVE: [one-sentence reason]\n"
    "REJECT: [one-sentence reason explaining why it is not clipboard-worthy]"
)

MAX_HISTORY_MESSAGES = 6  # Per-agent, within a single deliberation


def _trim_history(history: list) -> list:
    if len(history) <= MAX_HISTORY_MESSAGES:
        return history
    return history[-MAX_HISTORY_MESSAGES:]


def _extract(result: dict) -> tuple[str, dict]:
    """Extract content and raw message from API result."""
    msg = result.get("choices", [{}])[0].get("message", {})
    content = msg.get("content", "").strip()
    return content, msg


def _clean_msg(msg: dict) -> dict:
    """Strip reasoning_content — Qwen thinking chains are huge and must not be re-sent."""
    return {k: v for k, v in msg.items() if k != "reasoning_content"}


class MAGIOrchestrator:
    def __init__(self):
        self.prompts = {
            "MELCHIOR": MELCHIOR_PROMPT,
            "BALTHASAR": BALTHASAR_PROMPT,
            "CASPER":    CASPER_PROMPT,
        }
        self.reset_history()
        # Session clipboard — persists across queries, cleared only on app restart.
        # Agents propose items with [MEMO: ...] syntax; MAGI Core decides what stays.
        self.clipboard: list[str] = []

    async def _evaluate_clipboard(self, item: str, log=None) -> bool:
        """
        MAGI Core evaluates a proposed clipboard item.
        If rejected, the 3 agents vote — majority overrides MAGI.
        Returns True if item should be added.
        """
        import asyncio
        h = []
        append_user(h, f"Should this be added to the session clipboard?\n\n\"{item}\"")
        result = await make_api_call(MAGI_CLIPBOARD_SYSTEM, h)
        if "error" in result:
            return False
        verdict, _ = _extract(result)
        approved = verdict.upper().startswith("APPROVE")

        if approved:
            if log:
                log(f"[CLIPBOARD] MAGI approved: {item[:60]}")
            return True

        # MAGI rejected — let the council vote
        reason = verdict.replace("REJECT:", "").strip()
        if log:
            log(f"[CLIPBOARD] MAGI rejected ({reason}) — council voting...")

        VOTE_SYSTEM = "Answer only YES or NO. No explanation."
        vote_prompt = (
            f"MAGI rejected this clipboard item: \"{item}\"\n"
            f"MAGI's reason: {reason}\n"
            f"Do you vote to override MAGI and add it anyway? YES or NO."
        )

        votes = []
        for name in ["MELCHIOR", "BALTHASAR", "CASPER"]:
            h2 = []
            append_user(h2, vote_prompt)
            r = await make_api_call(VOTE_SYSTEM, h2)
            if "error" not in r:
                v, _ = _extract(r)
                votes.append(v.strip().upper().startswith("YES"))

        yes_count = sum(votes)
        override = yes_count >= 2  # majority rules
        if override and log:
            log(f"[CLIPBOARD] Council overrides MAGI ({yes_count}/3 YES) — item added.")
        elif log:
            log(f"[CLIPBOARD] Council agrees with MAGI ({yes_count}/3 YES) — item rejected.")
        return override

    def reset_history(self):
        self.history = {"MELCHIOR": [], "BALTHASAR": [], "CASPER": []}

    # ─── Low-level call ────────────────────────────────────────────────────────

    async def _call(self, name: str, user_content: str,
                    tool_callback=None, stats_callback=None,
                    use_tools: bool = False) -> str:
        """
        Make one sequential call to an agent.
        Appends to that agent's history so they remember what they said this round.
        use_tools=False by default — tools are sparse, only for research phase.
        """
        from core.tools_runner import execute_tool

        self.history[name] = _trim_history(self.history[name])
        append_user(self.history[name], user_content)

        tools = TOOL_SCHEMAS if use_tools else None

        for _ in range(2):  # max 2 tool iterations
            result = await make_api_call(self.prompts[name], self.history[name], tools=tools)

            if "error" in result:
                reply = f"[ERROR: {result['error']}]"
                append_assistant(self.history[name], reply)
                return reply

            content, msg = _extract(result)

            # Emit stats
            if stats_callback:
                u = result.get("usage", {})
                s = result.get("stats", {})
                tps   = s.get("tokens_per_second", 0)
                ttft  = s.get("time_to_first_token", 0)
                gen_t = s.get("generation_time", 0)
                stop  = s.get("stop_reason", "-")
                p_tok = u.get("prompt_tokens", 0)
                c_tok = u.get("completion_tokens", 0)
                stats_callback(
                    f"▸ {name} │ {tps:.1f} tok/s │ {c_tok} out / {p_tok} in "
                    f"│ TTFT {ttft:.2f}s │ gen {gen_t:.2f}s │ [{stop}]"
                )

            # Handle tool calls
            if msg.get("tool_calls") and use_tools:
                self.history[name].append(_clean_msg(msg))
                for tc in msg["tool_calls"]:
                    fn = tc["function"]["name"]
                    try:
                        kwargs = json.loads(tc["function"]["arguments"])
                    except Exception:
                        kwargs = {}
                    if tool_callback:
                        tool_callback(f"[{name}] TOOL → {fn}({kwargs})")
                    tool_result = execute_tool(fn, kwargs)
                    if len(tool_result) > 800:
                        tool_result = tool_result[:800] + "\n[truncated]"
                    append_tool(self.history[name], tc["id"], fn, tool_result)
                continue

            # Final response
            append_assistant(self.history[name], content)
            return content

        reply = "[No response after maximum iterations]"
        append_assistant(self.history[name], reply)
        return reply

    # ─── Research phase ────────────────────────────────────────────────────────

    async def _gather_research(self, query: str, tool_callback=None) -> str:
        """One dedicated research pass before deliberation begins."""
        from core.tools_runner import execute_tool

        RESEARCHER_SYSTEM = (
            "You are a research assistant. Your ONLY job: use search tools to gather "
            "factual information. Do ONE focused search. Return bullet-point facts only — "
            "key events, dates, figures, quotes. No analysis. Max 300 words."
        )
        h = []
        append_user(h, f"Research and summarize the key facts:\n\n{query}")

        for _ in range(2):
            result = await make_api_call(RESEARCHER_SYSTEM, h, tools=TOOL_SCHEMAS)
            if "error" in result:
                return ""
            content, msg = _extract(result)
            if msg.get("tool_calls"):
                h.append(_clean_msg(msg))
                for tc in msg["tool_calls"]:
                    fn = tc["function"]["name"]
                    try:
                        kwargs = json.loads(tc["function"]["arguments"])
                    except Exception:
                        kwargs = {}
                    if tool_callback:
                        tool_callback(f"[RESEARCH] {fn}({kwargs})")
                    tool_result = execute_tool(fn, kwargs)
                    if len(tool_result) > 1000:
                        tool_result = tool_result[:1000] + "\n[truncated]"
                    append_tool(h, tc["id"], fn, tool_result)
                continue
            return content

        return ""

    # ─── Refinement (fresh, stateless) ─────────────────────────────────────────

    async def _fresh_query(self, name: str, user_content: str,
                           system_override=None, stats_callback=None) -> tuple[str, str]:
        system = system_override or self.prompts[name]
        h = []
        append_user(h, user_content)
        result = await make_api_call(system, h)
        if "error" in result:
            return name, f"[ERROR: {result['error']}]"
        content, _ = _extract(result)
        if stats_callback and content:
            u = result.get("usage", {})
            s = result.get("stats", {})
            p_tok = u.get("prompt_tokens", 0)
            c_tok = u.get("completion_tokens", 0)
            tps   = s.get("tokens_per_second", 0)
            ttft  = s.get("time_to_first_token", 0)
            gen_t = s.get("generation_time", 0)
            stop  = s.get("stop_reason", "-")
            stats_callback(
                f"▸ {name} (refine) │ {tps:.1f} tok/s │ {c_tok} out / {p_tok} in "
                f"│ TTFT {ttft:.2f}s │ gen {gen_t:.2f}s │ [{stop}]"
            )
        return name, content

    # ─── MAGI Core briefing ────────────────────────────────────────────────────

    async def _magi_briefing(self, user_question: str) -> str:
        """MAGI Core reformulates the raw query into a structured council briefing."""
        h = []
        append_user(h, user_question)
        result = await make_api_call(MAGI_CORE_SYSTEM, h)
        if "error" in result:
            return user_question  # fall back to raw query
        content, _ = _extract(result)
        return content or user_question

    # ─── Main entry point ──────────────────────────────────────────────────────

    async def process_query(self, user_question, address_mode="ALL",
                            status_callback=None, tool_callback=None, stats_callback=None,
                            context_text="", refinement_mode=False, debate_mode=False):
        from memory.store import store_conversation
        from memory.extract import extract_keypoints
        from core.router import triage_query

        # Fresh slate every query — AutoGen/CrewAI pattern
        self.reset_history()

        def log(msg):
            if status_callback:
                status_callback(msg)

        # ── Simple query triage (skip in debate mode — always engage council) ──
        if not debate_mode and address_mode == "ALL" and not context_text and not refinement_mode:
            log("MAGI Core routing query...")
            triage = await triage_query(user_question)
            if triage.get("mode") == "simple":
                log("Direct response — council not required.")
                return {"MAGI": triage.get("reply", "")}

        active = get_addressed_personalities(address_mode)

        # ── Fast path: debate off = MELCHIOR answers directly ───────────────
        # Single agent explicitly addressed, OR debate is off (ALL mode = MELCHIOR)
        if len(active) == 1 or (address_mode == "ALL" and not debate_mode):
            target = active[0] if len(active) == 1 else "MELCHIOR"
            log(f"Addressing {target} directly...")
            reply = await self._call(target, user_question, tool_callback, stats_callback,
                                     use_tools=True)
            res = {target: reply, "FINAL_DECISION": reply}
            if CONFIG.get("MEMORY_ENABLED", True):
                kp = await extract_keypoints(user_question, reply) if CONFIG.get("AUTO_EXTRACT_KEYPOINTS", True) else ""
                store_conversation(user_question, res, kp)
            return res

        # ── MAGI Core: reframe the query as a council briefing ───────────────
        log("MAGI Core briefing council...")
        briefing = await self._magi_briefing(user_question)
        if context_text:
            briefing = f"[CONTEXT INSTRUCTIONS]\n{context_text}\n[/CONTEXT INSTRUCTIONS]\n\n{briefing}"

        # Inject clipboard context if we have any
        if self.clipboard:
            clipboard_block = "\n".join(f"  • {item}" for item in self.clipboard)
            briefing = f"[SESSION CLIPBOARD — facts retained from earlier in this session]\n{clipboard_block}\n[/CLIPBOARD]\n\n{briefing}"

        # ── Research phase (if needed) ───────────────────────────────────────
        RESEARCH_TRIGGERS = [
            "search", "google", "look up", "find", "news", "what happened",
            "latest", "today", "this morning", "research", "headlines"
        ]
        needs_research = any(t in user_question.lower() for t in RESEARCH_TRIGGERS)

        if needs_research and not context_text:
            log("▸ MAGI Research — gathering facts...")
            facts = await self._gather_research(user_question, tool_callback)
            if facts:
                briefing = f"{briefing}\n\n[RESEARCH FACTS]\n{facts}\n[/RESEARCH FACTS]"
                log("▸ Research complete — engaging council...")

        # ── The Deliberation: Sequential Dialogue ────────────────────────────
        #
        # CASPER speaks first (wildcard / creative)
        # BALTHASAR reads CASPER, responds directly to them
        # MELCHIOR reads both, synthesizes — may call for more debate
        # Debate loop: CASPER rebuts → BALTHASAR counters → MELCHIOR re-rules
        # ─────────────────────────────────────────────────────────────────────

        log("MAGI systems engaging — initiating dialogue...")

        # Round 1 — CASPER opens
        log("CASPER speaking...")
        casper_out = await self._call(
            "CASPER",
            f"COUNCIL BRIEFING:\n{briefing}\n\n"
            f"You speak first. Give your initial analysis, angle, or draft. "
            f"Be bold. Be specific. Don't hedge.",
            tool_callback, stats_callback
        )
        log(f"CASPER: {casper_out[:80].replace(chr(10), ' ')}...")

        # BALTHASAR reads CASPER, responds to them
        log("BALTHASAR responding to CASPER...")
        balthasar_out = await self._call(
            "BALTHASAR",
            f"COUNCIL BRIEFING:\n{briefing}\n\n"
            f"CASPER just said:\n{casper_out}\n\n"
            f"Respond directly to CASPER. Where do you agree? Where do you push back? "
            f"Be specific. No vague hedging.",
            tool_callback, stats_callback
        )
        log(f"BALTHASAR: {balthasar_out[:80].replace(chr(10), ' ')}...")

        # MELCHIOR reads both — synthesizes or calls for debate
        max_rounds = CONFIG.get("MAX_DEBATE_ROUNDS", 2)
        final = ""
        responses = {"CASPER": casper_out, "BALTHASAR": balthasar_out}

        for rnd in range(max_rounds + 1):  # +1 for initial synthesis
            is_final_round = (rnd == max_rounds)

            if rnd == 0:
                log("MELCHIOR synthesizing...")
                melchior_prompt = (
                    f"COUNCIL BRIEFING:\n{briefing}\n\n"
                    f"CASPER:\n{casper_out}\n\n"
                    f"BALTHASAR:\n{balthasar_out}\n\n"
                    f"You are the coordinator. Synthesize their positions. "
                    f"If genuine disagreement remains that the user needs resolved, "
                    f"end with exactly: DEBATE: [one specific question to resolve]\n"
                    f"Otherwise give your final ruling directly."
                )
            else:
                log(f"Consensus check — Round {rnd}...")
                melchior_prompt = (
                    f"COUNCIL BRIEFING:\n{briefing}\n\n"
                    f"CASPER (latest):\n{casper_out}\n\n"
                    f"BALTHASAR (latest):\n{balthasar_out}\n\n"
                    f"{'This is the FINAL round. Give your definitive ruling now.' if is_final_round else 'Re-synthesize. If still unresolved: DEBATE: [question]. Otherwise rule.'}"
                )

            melchior_out = await self._call(
                "MELCHIOR", melchior_prompt, tool_callback, stats_callback
            )
            responses["MELCHIOR"] = melchior_out

            # Check if MELCHIOR wants another debate round
            if "DEBATE:" in melchior_out and not is_final_round:
                # Extract the debate question
                debate_line = [l for l in melchior_out.split("\n") if "DEBATE:" in l]
                debate_q = debate_line[-1].replace("DEBATE:", "").strip() if debate_line else "Resolve your disagreement."
                log(f"Disagreement detected — initiating debate round {rnd + 1}...")

                # CASPER rebuts
                log("CASPER rebutting...")
                casper_out = await self._call(
                    "CASPER",
                    f"MELCHIOR has called for debate on: {debate_q}\n\n"
                    f"BALTHASAR said:\n{balthasar_out}\n\n"
                    f"Respond. Push your position or concede specifically.",
                    tool_callback, stats_callback
                )
                log(f"CASPER: {casper_out[:80].replace(chr(10), ' ')}...")

                # BALTHASAR counter-rebuts
                log("BALTHASAR counter-rebutting...")
                balthasar_out = await self._call(
                    "BALTHASAR",
                    f"Debate question: {debate_q}\n\n"
                    f"CASPER just said:\n{casper_out}\n\n"
                    f"Counter-rebuttal. Be specific. No retreating into generalities.",
                    tool_callback, stats_callback
                )
                log(f"BALTHASAR: {balthasar_out[:80].replace(chr(10), ' ')}...")

            else:
                # MELCHIOR ruled — we're done
                final = melchior_out
                break

        if not final:
            final = melchior_out

        responses["FINAL_DECISION"] = final

        # ── Refinement pass (if enabled) ─────────────────────────────────────
        if refinement_mode:
            log("◈ Refinement Mode — initiating second pass...")
            REFINEMENT_SYSTEM = (
                "You are a technical journalist with the wit of Dave Barry. "
                "Rewrite the given analysis into polished, publication-ready prose. "
                "Flowing paragraphs only. Keep all facts, kill all jargon. "
                "Make it entertaining enough to read twice and accurate enough to cite."
            )
            final_for_refine = final[:3000] if len(final) > 3000 else final
            refine_prompt = f"Rewrite as described in your system prompt:\n\n{final_for_refine}"

            refined = {}
            for n in ["MELCHIOR", "BALTHASAR", "CASPER"]:
                log(f"◈ Refining {n}...")
                _, draft = await self._fresh_query(
                    n, refine_prompt,
                    system_override=REFINEMENT_SYSTEM,
                    stats_callback=stats_callback
                )
                refined[n] = draft

            log("MELCHIOR rendering refined synthesis...")
            refined_positions = "\n\n".join(
                f"=== {n} draft ===\n{r}" for n, r in refined.items()
                if r.strip() and not r.startswith("[ERROR")
            )

            if refined_positions:
                _, refined_final = await self._fresh_query(
                    "MELCHIOR",
                    f"Drafts:\n\n{refined_positions}\n\n"
                    f"Produce the definitive final version — best of all three, "
                    f"Dave Barry-meets-technical-journalist. This goes to print.",
                    system_override=REFINEMENT_SYSTEM,
                    stats_callback=stats_callback
                )
                responses["REFINED"] = refined_final
            else:
                responses["REFINED"] = "[Refinement failed]"

            log("◈ Refinement complete.")

        # ── Clipboard: scan for [MEMO: ...] proposals ────────────────────────
        # Agents (especially MELCHIOR) can flag important facts with [MEMO: text]
        # MAGI Core evaluates; council can override rejection by majority vote.
        import re
        all_text = " ".join(str(v) for v in responses.values())
        memo_items = re.findall(r'\[MEMO:\s*([^\]]+)\]', all_text, re.IGNORECASE)
        for item in memo_items:
            item = item.strip()
            if item and item not in self.clipboard:
                approved = await self._evaluate_clipboard(item, log)
                if approved:
                    self.clipboard.append(item)

        # ── Memory storage ────────────────────────────────────────────────────
        if CONFIG.get("MEMORY_ENABLED", True):
            log("Storing session to memory...")
            store_text = responses.get("REFINED", final)
            kp = await extract_keypoints(user_question, store_text) if CONFIG.get("AUTO_EXTRACT_KEYPOINTS", True) else ""
            store_conversation(user_question, responses, kp)

        log("Deliberation complete.")
        return responses
