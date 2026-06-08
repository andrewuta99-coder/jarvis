// Host registry — one entry per supported AI agent.
//
// Adding a new host:
//   1. Create hosts/<name>.ts with a HostConfig export
//   2. Add the import + entry below
//   3. Add a case in setup script's host switch (for skillsRoot)
//
// Mirror of gstack/hosts/index.ts.

export interface HostConfig {
  /** Canonical name. Used as ./setup --host <name>. */
  name: string;
  /** Where skills get symlinked. ~/ allowed. */
  skillsRoot: string;
  /** Prefix to apply to skill directory names. e.g., "jarvis-" -> /jarvis-init. */
  skillPrefix: string;
  /** SKILL file extension. ".md" for all hosts at v0. */
  fileExtension: string;
  /** Frontmatter format. "yaml" for all hosts at v0. */
  frontmatterFormat: "yaml" | "toml" | "json";
  /** Does this host support Claude Code's Agent tool for parallel sub-agents? */
  supportsAgentTool: boolean;
  /** AskUserQuestion native tool? */
  supportsAskUserQuestion: boolean;
  /** MCP server support? */
  supportsMcp: boolean;
  /** Host-specific notes for the setup output. */
  notes: string[];
}

import { claude } from "./claude";
import { codex } from "./codex";
import { cursor } from "./cursor";
import { openclaw } from "./openclaw";

export const hosts: Record<string, HostConfig> = {
  claude,
  codex,
  cursor,
  openclaw,
};

export type Host = keyof typeof hosts;
