import type { HostConfig } from "./index";

export const codex: HostConfig = {
  name: "codex",
  skillsRoot: "~/.codex/skills",
  skillPrefix: "jarvis-",
  fileExtension: ".md",
  frontmatterFormat: "yaml",
  supportsAgentTool: false,   // v0: Codex CLI does not yet support parallel sub-agents
  supportsAskUserQuestion: false,
  supportsMcp: false,
  notes: [
    "Single-session execution. The orchestrator runs all specialists sequentially.",
    "Init takes ~3x longer than Claude due to no parallelism.",
    "AskUserQuestion calls degrade to inline prompts in stdout.",
  ],
};
