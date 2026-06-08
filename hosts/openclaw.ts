import type { HostConfig } from "./index";

export const openclaw: HostConfig = {
  name: "openclaw",
  skillsRoot: "~/.openclaw/skills",
  skillPrefix: "jarvis-",
  fileExtension: ".md",
  frontmatterFormat: "yaml",
  supportsAgentTool: false,  // OpenClaw spawns Claude Code sessions for execution
  supportsAskUserQuestion: false,
  supportsMcp: false,
  notes: [
    "OpenClaw orchestrator pattern: native conversational skills run in OpenClaw,",
    "execution skills spawn Claude Code sessions via ACP. See docs/OPENCLAW.md.",
    "Spawned sessions get OPENCLAW_SESSION=1 env var and skip interactive prompts.",
  ],
};
