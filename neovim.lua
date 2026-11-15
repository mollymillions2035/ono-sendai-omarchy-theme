-- Ono-Sendai for LazyVim. Omarchy would otherwise generate this file from
-- colors.toml (default/themed/neovim.lua.tpl): aether.nvim with the palette
-- below. This one keeps that and retunes the highlights to the house style of
-- fish.theme and opencode-desktop.json: Ono-Sendai red for functions, titles,
-- borders and the cursor line number, bright red keywords, warm orange strings,
-- and red instead of aether's blue wherever the editor marks something.
-- The palette is a copy of colors.toml; keep the two in step.
return {
  {
    "omacom/aether.nvim",
    branch = "v3",
    name = "aether",
    priority = 1000,
    opts = {
      colors = {
        bg = "#0a0707",
        dark_bg = "#070505",
        darker_bg = "#040303",
        lighter_bg = "#160e0d",

        fg = "#e6d9d4",
        dark_fg = "#6e5f5b",
        light_fg = "#b8a8a3",
        bright_fg = "#f7eeea",
        muted = "#64504b",

        red = "#e8261b",
        yellow = "#e3b24f",
        orange = "#ee6a2c",
        green = "#8ab36f",
        cyan = "#5fb0aa",
        blue = "#7489c4",
        magenta = "#cf5a86",
        brown = "#8c4632",

        bright_red = "#ff5a4c",
        bright_yellow = "#f0cd82",
        bright_green = "#aed095",
        bright_cyan = "#8fd0ca",
        bright_blue = "#a2b2e0",
        bright_magenta = "#e68bab",

        accent = "#e8261b",
        cursor = "#f7eeea",
        foreground = "#e6d9d4",
        background = "#0a0707",
        selection = "#3b1411",
        selection_foreground = "#f7eeea",
        selection_background = "#3b1411",
      },
      styles = {
        comments = { italic = true },
        keywords = {},
      },
      on_colors = function(c)
        c.border_highlight = c.red
        c.bg_search = c.selection
        c.cursorline_bg = c.lighter_bg
        c.todo = c.bright_yellow
      end,
      on_highlights = function(hl, c)
        local comment = "#8f7d78" -- muted ink that still reads on deck black
        local string = "#f6925e" -- bright orange, as fish quotes
        local set = function(groups, spec)
          for _, group in ipairs(groups) do
            hl[group] = spec
          end
        end

        -- Syntax
        set({ "Comment", "SpecialComment" }, { fg = comment, italic = true })
        set({ "Keyword", "Conditional", "Repeat", "Exception", "Define", "Statement", "Include" }, { fg = c.bright_red })
        set({ "@keyword", "@keyword.function" }, { fg = c.bright_red })
        set({ "Function" }, { fg = c.red, bold = true })
        set({ "@function.call", "@function.method.call", "@function.builtin", "@constructor" }, { fg = c.red })
        set({ "String", "Character" }, { fg = string })
        set({ "@string.documentation" }, { fg = comment })
        set({ "@string.escape", "SpecialChar" }, { fg = c.cyan })
        set({ "Number", "Boolean", "Float", "@constant.builtin" }, { fg = c.bright_magenta })
        set({ "Constant" }, { fg = c.bright_blue })
        set({ "Type", "StorageClass", "Structure", "Typedef" }, { fg = c.bright_yellow })
        set({ "@type.builtin" }, { fg = c.yellow })
        set({ "Identifier", "@property", "@variable.member" }, { fg = c.cyan })
        set({ "@variable.parameter" }, { fg = c.light_fg })
        set({ "@variable.builtin", "@module.builtin" }, { fg = c.bright_red })
        set({ "@module" }, { fg = c.light_fg })
        set({ "Operator", "@operator", "@punctuation.special" }, { fg = c.yellow })
        set({ "PreProc", "Macro", "PreCondit" }, { fg = c.orange })
        set({ "Tag", "@tag", "@tag.tsx", "@tag.javascript", "Label", "@label" }, { fg = c.red })
        set({ "@tag.delimiter.tsx" }, { fg = c.dark_fg })

        -- Editor
        set({ "CursorLineNr" }, { fg = c.red, bold = true })
        set({ "MatchParen" }, { fg = c.bright_red, bold = true, underline = true })
        set({ "Search" }, { bg = c.selection, fg = c.bright_fg, bold = true })
        set({ "IncSearch" }, { bg = c.red, fg = c.darker_bg, bold = true })
        set({ "Substitute" }, { bg = c.bright_red, fg = c.darker_bg })
        set({ "Title", "Directory", "MoreMsg", "Question" }, { fg = c.red, bold = true })
        set({ "PmenuSel" }, { bg = c.selection, fg = c.bright_fg })
        set({ "PmenuMatch" }, { bg = c.bg_popup, fg = c.bright_red })
        set({ "PmenuMatchSel" }, { bg = c.selection, fg = c.bright_red })
        set({ "TabLineSel" }, { fg = c.darker_bg, bg = c.red })
        set({ "Folded" }, { fg = c.light_fg, bg = c.lighter_bg, italic = true })
        set({ "Todo" }, { bg = c.red, fg = c.darker_bg, bold = true })
        set({ "htmlH1", "htmlH2" }, { fg = c.red, bold = true })
        set({ "qfFileName", "diffFile", "diffIndexLine" }, { fg = c.red })
        set({ "diffOldFile" }, { fg = c.bright_red, bg = c.diff.delete })
        set({ "diffNewFile" }, { fg = c.bright_green, bg = c.diff.add })
        set({ "helpCommand" }, { bg = c.subtle_bg, fg = string })

        -- Markdown
        set({ "@markup.heading.5.markdown" }, { fg = c.red, bold = true })
        set({ "@markup.link", "@markup.link.label" }, { fg = c.bright_red, underline = true })
        set({ "@markup.raw.markdown_inline" }, { bg = c.lighter_bg, fg = string })
        set({ "@markup.list.markdown", "@punctuation.special.markdown" }, { fg = c.red, bold = true })

        -- Plugins LazyVim ships
        set({ "WhichKeyGroup", "BlinkCmpLabelMatch", "BlinkCmpSignatureHelpActiveParameter" }, { fg = c.red, bold = true })
        set({ "NoiceCmdlineIcon", "NeoTreeDirectoryIcon" }, { fg = c.red })
        set({ "NeoTreeDirectoryName" }, { fg = c.fg })
        set({ "NeoTreeRootName", "MiniStarterHeader", "MiniStarterSection" }, { fg = c.red, bold = true })
        set({ "NeoTreeTabActive" }, { fg = c.red, bg = c.dark_bg, bold = true })
        set({ "NeoTreeTabSeparatorActive" }, { fg = c.red, bg = c.dark_bg })
        set({ "MiniIndentscopeSymbol" }, { fg = c.red, nocombine = true })
        set({ "MiniStatuslineModeNormal", "MiniTablineTabpagesection" }, { fg = c.darker_bg, bg = c.red, bold = true })
      end,
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "aether",
    },
  },
}
