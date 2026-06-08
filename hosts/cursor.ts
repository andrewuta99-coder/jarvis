import type { HostConfig } from "./index";

export const cursor: HostConfig = {
  name: "cursor",
  skillsRoot: "~/.cursor/skills",
  skillPrefix: "jarvis-",
  fileExtension: ".md",
  frontmatterFormat: "yaml",
  supportsAgentTool: true,  // Cursor's Agent tab supports parallel sub-agents
  supportsAskUserQuestion: true,
  supportsMcp: true,
  notes: [
    "Cursor Composer + Agent mode. Use Agent mode for /jarvis-init (needs Agent tool).",
  ],
};
