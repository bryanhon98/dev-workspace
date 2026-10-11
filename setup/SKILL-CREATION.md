# Creating or improving a skill

The global rules require this workflow whenever the user asks to create or update a skill, including custom personal skills.

1. Establish the job, trigger conditions, expected output and success criteria from the conversation.
2. Draft concise SKILL.md instructions with name and description metadata and only the supporting resources needed.
3. Inspect executable support files; try realistic prompts and relevant edge cases in an isolated location. Check triggering and output quality. Compare with the previous version or a baseline where useful.
4. Improve the draft based on results and retest affected behavior.
5. Run SkillSpector and review supporting code before global installation. Verify installation, save the reviewed version and tests, and publish its installation record.

Preferred reference: [Anthropic's official skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator). Its draft/test/evaluate/improve loop was read when adding this policy on 2026-10-12 (Asia/Kuala_Lumpur). This is a reference, not an installed or audited copy. Review and pin it before installing or running its bundled scripts. Claude-specific commands and evaluation tools may need adaptation to Codex.

Alternative: the built-in Codex $skill-creator, when exposed by the current client. The literal Claude command /skill-creator is not assumed available in Codex. If no creator is callable, follow the workflow above directly and say so.

Official Codex references:
- [Skill format, creator and user-global discovery](https://learn.chatgpt.com/docs/build-skills)
- [Global instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

Neither a creator nor a scanner guarantees a good skill. Behavior checks measure usefulness; inspection reviews risks. Retain evidence for both when applicable.
