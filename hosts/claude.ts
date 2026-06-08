// Host config for Claude Code.
// Pattern mirrors gstack/hosts/claude.ts.

import type { HostConfig } from "./index";

export const claude: HostConfig = {
  name: "claude",
  skillsRoot: "~/.claude/skills",
  skillPrefix: "jarvis-",  // skills appear as /jarvis-init, /jarvis-add-users, etc.
  fileExtension: ".md",    // SKILL.md
  frontmatterFormat: "yaml",
  supportsAgentTool: true, // can spawn parallel subagents via Agent()
  supportsAskUserQuestion: true,
  supportsMcp: true,
  notes: [
    "Primary host. Full feature set: Agent, AskUserQuestion, MCP, plan mode.",
    "Skill names installed without prefix by default. Use ./setup --prefix to add 'jarvis-'.",
  ],
};
