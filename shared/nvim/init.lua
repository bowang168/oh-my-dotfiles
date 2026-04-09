-- ===========================================
-- Neovim Config - migrated from .vimrc + enhancements
-- ===========================================

-- Leader key (set before plugins)
vim.g.mapleader = " "
vim.g.maplocalleader = " "

-- ===========================================
-- General Settings
-- ===========================================
vim.opt.encoding = "utf-8"
vim.opt.fileencoding = "utf-8"
vim.opt.clipboard = "unnamedplus"   -- System clipboard integration
vim.opt.mouse = "a"                 -- Mouse support
vim.opt.undofile = true             -- Persistent undo across sessions
vim.opt.swapfile = false            -- No .swp files cluttering projects
vim.opt.backup = false

-- ===========================================
-- Interface
-- ===========================================
vim.opt.number = true               -- Line numbers
vim.opt.relativenumber = true       -- Relative line numbers
vim.opt.cursorline = true           -- Highlight current line
vim.opt.showmatch = true            -- Highlight matching brackets
vim.opt.wildmenu = true             -- Enhanced command completion
vim.opt.showcmd = true
vim.opt.ruler = true
vim.opt.signcolumn = "yes"          -- Always show sign column (git, diagnostics)
vim.opt.scrolloff = 8               -- Keep 8 lines visible above/below cursor
vim.opt.sidescrolloff = 8
vim.opt.termguicolors = true        -- True color support
vim.opt.splitbelow = true           -- Horizontal splits open below
vim.opt.splitright = true           -- Vertical splits open right

-- ===========================================
-- Search
-- ===========================================
vim.opt.hlsearch = true
vim.opt.incsearch = true
vim.opt.ignorecase = true
vim.opt.smartcase = true

-- ===========================================
-- Indentation
-- ===========================================
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.expandtab = true
vim.opt.autoindent = true
vim.opt.smartindent = true

-- ===========================================
-- Performance
-- ===========================================
vim.opt.lazyredraw = true
vim.opt.updatetime = 250
vim.opt.timeoutlen = 300

-- ===========================================
-- Plugin Manager: lazy.nvim
-- ===========================================
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.uv.fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
  -- Colorscheme
  {
    "catppuccin/nvim",
    name = "catppuccin",
    priority = 1000,
    config = function()
      -- Read theme from ~/.theme_mode (set by ~/bin/theme script)
      local mode = "dark"
      local f = io.open(os.getenv("HOME") .. "/.theme_mode", "r")
      if f then mode = f:read("*l") or "dark"; f:close() end
      local is_dark = mode ~= "light"
      vim.o.background = is_dark and "dark" or "light"
      vim.cmd.colorscheme(is_dark and "catppuccin-mocha" or "catppuccin-latte")
    end,
  },

  -- File explorer
  {
    "nvim-tree/nvim-tree.lua",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("nvim-tree").setup({
        filters = { dotfiles = true },
      })
    end,
  },

  -- Fuzzy finder (fzf integration)
  {
    "ibhagwan/fzf-lua",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("fzf-lua").setup()
    end,
  },

  -- Status line
  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("lualine").setup({
        options = { theme = "auto" },
      })
    end,
  },

  -- Git signs in gutter
  {
    "lewis6991/gitsigns.nvim",
    config = function()
      require("gitsigns").setup()
    end,
  },

  -- Surround (quotes, brackets)
  { "kylechui/nvim-surround", event = "VeryLazy", config = true },

  -- Auto pairs
  { "windwp/nvim-autopairs", event = "InsertEnter", config = true },

  -- Comment toggle (gcc / gc)
  { "numToStr/Comment.nvim", event = "VeryLazy", config = true },

  -- Treesitter (syntax highlighting)
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    config = function()
      require("nvim-treesitter").setup({
        ensure_installed = { "lua", "python", "bash", "json", "yaml", "markdown", "vim", "vimdoc" },
      })
    end,
  },

  -- Which-key (show keybinding hints)
  {
    "folke/which-key.nvim",
    event = "VeryLazy",
    config = true,
  },

  -- Markdown preview in browser
  {
    "iamcco/markdown-preview.nvim",
    cmd = { "MarkdownPreview", "MarkdownPreviewStop", "MarkdownPreviewToggle" },
    ft = { "markdown" },
    build = "cd app && npx --yes yarn install",
  },
})

-- ===========================================
-- Keymaps
-- ===========================================
local map = vim.keymap.set

-- Clear search highlight with Esc
map("n", "<Esc>", "<cmd>nohlsearch<CR>")

-- File explorer
map("n", "<leader>e", "<cmd>NvimTreeToggle<CR>", { desc = "File explorer" })

-- Fuzzy finder
map("n", "<leader>ff", "<cmd>FzfLua files<CR>", { desc = "Find files" })
map("n", "<leader>fg", "<cmd>FzfLua live_grep<CR>", { desc = "Live grep" })
map("n", "<leader>fb", "<cmd>FzfLua buffers<CR>", { desc = "Buffers" })
map("n", "<leader>fh", "<cmd>FzfLua help_tags<CR>", { desc = "Help tags" })
map("n", "<leader>fr", "<cmd>FzfLua oldfiles<CR>", { desc = "Recent files" })

-- Window navigation
map("n", "<C-h>", "<C-w>h", { desc = "Move to left window" })
map("n", "<C-j>", "<C-w>j", { desc = "Move to lower window" })
map("n", "<C-k>", "<C-w>k", { desc = "Move to upper window" })
map("n", "<C-l>", "<C-w>l", { desc = "Move to right window" })

-- Move lines up/down in visual mode
map("v", "J", ":m '>+1<CR>gv=gv", { desc = "Move line down" })
map("v", "K", ":m '<-2<CR>gv=gv", { desc = "Move line up" })

-- Better indenting (stay in visual mode)
map("v", "<", "<gv")
map("v", ">", ">gv")

-- Markdown preview
map("n", "<leader>mp", "<cmd>MarkdownPreviewToggle<CR>", { desc = "Markdown preview" })
