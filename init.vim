" vimrc
" Author: Robbie Iannucci <robbie@rail.com>
" Source: https://github.com/riannucci/vimified
" Original Author: Zaiste! <oh@zaiste.net>
" Original Source: https://github.com/zaiste/vimified
"
" Have fun!
"

let mapleader = ","
let maplocalleader = "\\"

packadd cfilter

let &spellfile=expand('<sfile>:p:h') . '/dict.utf-8.add'

call plug#begin('~/.config/nvim/plugged')

Plug 'airblade/vim-gitgutter'
Plug 'bronson/vim-visual-star-search'
Plug 'ehamberg/vim-cute-python', { 'branch': 'moresymbols' }
Plug 'fatih/vim-go', { 'do': ':GoUpdateBinaries' }
Plug 'HerringtonDarkholme/yats'
Plug 'hrsh7th/cmp-buffer'
Plug 'hrsh7th/cmp-nvim-lsp'
Plug 'hrsh7th/nvim-cmp'
Plug 'majutsushi/tagbar'
Plug 'mfussenegger/nvim-dap'
Plug 'mfussenegger/nvim-dap-python'
Plug 'neovim/nvim-lspconfig'
Plug 'nvim-treesitter/nvim-treesitter', {'do': ':TSUpdate'}
Plug 'quangnguyen30192/cmp-nvim-ultisnips'
Plug 'Raimondi/delimitMate'
Plug 'riannucci/vim-python-pep8-indent'
Plug 'SirVer/ultisnips'
Plug 'tpope/vim-fugitive'
Plug 'tpope/vim-repeat'
Plug 'tpope/vim-speeddating'
Plug 'tpope/vim-surround'
Plug 'tpope/vim-unimpaired'
Plug 'vim-airline/vim-airline'
Plug 'w0ng/vim-hybrid'

call plug#end()

"ultisnips
" Can't use <tab> as it conflicts with YCM.
let g:UltiSnipsExpandTrigger="<leader>."
let g:UltiSnipsJumpForwardTrigger="<c-b>"
let g:UltiSnipsJumpBackwardTrigger="<c-z>"

"pep8
let g:python_pep8_indent_multiline_string=-2  " textwrap.dedent style
let g:python_pep8_func_continuation=1

"airline
let g:airline_powerline_fonts=1

"tagbar
nmap <leader>t :TagbarToggle<CR>

"delimitMate
let g:delimitMate_expand_space = 1
let g:delimitMate_expand_cr = 1

autocmd FileType gitcommit set tw=68 spell



" lsp config
lua <<EOF
  -- Setup nvim-cmp.
  local cmp = require'cmp'

  cmp.setup({
    snippet = {
      expand = function(args)
        vim.fn["UltiSnips#Anon"](args.body)
      end,
    },
    mapping = {
      ['<Tab>'] = cmp.mapping(cmp.mapping.select_next_item(), { 'i', 's' }),
      ['<Down>'] = cmp.mapping(cmp.mapping.select_next_item(), { 'i', 's' }),
      ['<S-Tab>'] = cmp.mapping(cmp.mapping.select_prev_item(), { 'i', 's' }),
      ['<Up>'] = cmp.mapping(cmp.mapping.select_prev_item(), { 'i', 's' }),
      ['<C-d>'] = cmp.mapping.scroll_docs(-4),
      ['<C-f>'] = cmp.mapping.scroll_docs(4),
      ['<C-e>'] = cmp.mapping.close(),
      ['<CR>'] = cmp.mapping.confirm { select = true },
    },
    sources = {
      { name = 'nvim_lsp' },
      { name = 'ultisnips' },
      { name = 'buffer' },
    }
  })

  -- Setup lspconfig.
  require('lspconfig')['gopls'].setup {
    on_attach = function(client, bufnr)
      local function buf_set_keymap(...) vim.api.nvim_buf_set_keymap(bufnr, ...) end
      local function buf_set_option(...) vim.api.nvim_buf_set_option(bufnr, ...) end

      -- Enable completion triggered by <c-x><c-o>
      buf_set_option('omnifunc', 'v:lua.vim.lsp.omnifunc')

      -- Mappings.
      local opts = { noremap=true, silent=true }

      -- See `:help vim.lsp.*` for documentation on any of the below functions
      buf_set_keymap('n', '<space>', '<cmd>lua vim.lsp.buf.definition()<CR>', opts)
      buf_set_keymap('n', '<S-space>', '<cmd>lua vim.lsp.buf.declaration()<CR>', opts)
      buf_set_keymap('n', '<C-space>', '<cmd>lua vim.lsp.buf.type_definition()<CR>', opts)
      buf_set_keymap('n', '<leader>t', '<cmd>lua vim.lsp.buf.code_action()<CR>', opts)
      buf_set_keymap('n', '<leader>f', '<cmd>lua vim.lsp.buf.format()<CR>', opts)
    end,
    capabilities = require('cmp_nvim_lsp').default_capabilities(vim.lsp.protocol.make_client_capabilities()),
    settings = { gopls =  {
      env = {CGO_ENABLED="0"}
    }}
  }

  require('lspconfig')['pyright'].setup {
    on_attach = function(client, bufnr)
      local function buf_set_keymap(...) vim.api.nvim_buf_set_keymap(bufnr, ...) end
      local function buf_set_option(...) vim.api.nvim_buf_set_option(bufnr, ...) end

      -- Enable completion triggered by <c-x><c-o>
      buf_set_option('omnifunc', 'v:lua.vim.lsp.omnifunc')

      -- Mappings.
      local opts = { noremap=true, silent=true }

      -- See `:help vim.lsp.*` for documentation on any of the below functions
      buf_set_keymap('n', '<space>', '<cmd>lua vim.lsp.buf.definition()<CR>', opts)
      buf_set_keymap('n', '<S-space>', '<cmd>lua vim.lsp.buf.declaration()<CR>', opts)
      buf_set_keymap('n', '<C-space>', '<cmd>lua vim.lsp.buf.type_definition()<CR>', opts)
    end,
    capabilities = require('cmp_nvim_lsp').default_capabilities(vim.lsp.protocol.make_client_capabilities()),
  }
EOF


set background=dark
colorscheme hybrid

" Set 5 lines to the cursor - when moving vertically
set scrolloff=5

" Highlight VCS conflict markers
match ErrorMsg '^\(<\|=\|>\)\{7\}\([^=].\+\)\?$'

" clear highlight after search
noremap <silent><leader>/ :nohls<CR>

" Emacs bindings in command line mode
cnoremap <c-a> <home>
cnoremap <c-e> <end>

tnoremap <Esc><Esc> <C-\><C-n>

" Always copy/paste to/from the system clipboard
set clipboard+=unnamedplus

set cinoptions=:0,(s,u0,U1,g0,t0
set hidden
set list

" Disable the macvim toolbar
set guioptions-=T

set listchars=tab:▸\ ,eol:¬,extends:❯,precedes:❮,trail:␣
set showbreak=↪

set notimeout
set ttimeout
set ttimeoutlen=10

set noeol
set relativenumber
set number
set ruler
if executable('/bin/zsh')
  set shell=/bin/zsh
endif
set showcmd

set exrc
set secure

set matchtime=2

set completeopt=menu,menuone,noselect

set formatoptions+=rn1
"let &colorcolumn="+1,".join(range(120,320), ",")

set visualbell


set dictionary=/usr/share/dict/words

set tabstop=2
set textwidth=80
set shiftwidth=2
set softtabstop=2

" Stop the crazy margins :D
set numberwidth=2

" Modelines
set modeline
set modelines=5

set expandtab

set nowrap

set wildignore+=.svn,CVS,.git,.hg,*.o,*.a,*.class,*.mo,*.la,*.so,*.obj,*.swp,*.jpg,*.png,*.xpm,*.gif,.DS_Store,*.aux,*.out,*.toc,*.pyc,*.pb.go,*.gen.go,pb.discovery.go
set wildmode=list:longest,full

set tildeop

set guifont=DejaVu_Sans_Mono_for_Powerline:h11:cANSI

" Cursorline {{{
" Only show cursorline in the current window and in normal mode.
augroup cline
    au!
    au WinLeave * set nocursorline
    au WinEnter * set cursorline
    au InsertEnter * set nocursorline
    au InsertLeave * set cursorline
augroup END
" }}}

" Trailing whitespace {{{
" Only shown when not in insert mode so I don't go insane.
augroup trailing
    au!
    au InsertEnter * :set listchars-=trail:␣
    au InsertLeave * :set listchars+=trail:␣
augroup END

" Remove trailing whitespaces when saving
" Wanna know more? http://vim.wikia.com/wiki/Remove_unwanted_spaces
" If you want to remove trailing spaces when you want, so not automatically,
" see
" http://vim.wikia.com/wiki/Remove_unwanted_spaces#Display_or_remove_unwanted_whitespace_with_a_script.
autocmd BufWritePre * :%s/\s\+$//e

" }}}

" . searching {{{

set ignorecase
set smartcase
set showmatch
set gdefault

" Keep search matches in the middle of the window.
nnoremap n nzzzv
nnoremap N Nzzzv

" Open a Quickfix window for the last search.
nnoremap <silent> <leader>? :execute 'vimgrep /'.@/.'/g %'<CR>:copen<CR>

" Highlight word {{{

nnoremap <silent> <leader>hh :execute 'match InterestingWord1 /\<<c-r><c-w>\>/'<cr>
nnoremap <silent> <leader>h1 :execute 'match InterestingWord1 /\<<c-r><c-w>\>/'<cr>
nnoremap <silent> <leader>h2 :execute '2match InterestingWord2 /\<<c-r><c-w>\>/'<cr>
nnoremap <silent> <leader>h3 :execute '3match InterestingWord3 /\<<c-r><c-w>\>/'<cr>

" }}}

" }}}


" Buffer Handling {{{
" Visit http://vim.wikia.com/wiki/Deleting_a_buffer_without_closing_the_window
" to learn more about :Bclose

" Delete buffer while keeping window layout (don't close buffer's windows).
" Version 2008-11-18 from http://vim.wikia.com/wiki/VimTip165
if v:version < 700 || exists('loaded_bclose') || &cp
  finish
endif
let loaded_bclose = 1
if !exists('bclose_multiple')
  let bclose_multiple = 1
endif

" Tagbar mapping interferes with Align
nunmap <Leader>t
nmap   <Leader>, :TagbarToggle<CR>
let g:tagbar_autoclose=1

" Make Page keys only go by half the screen.
map! <PageUp> <C-U>
map! <PageDown> <C-F>

" Let's stick with hybrid for now
" colorscheme distinguished
hi! Operator guifg=#cc6666 ctermfg=9 guibg=NONE ctermbg=NONE gui=NONE term=NONE

if !has('mac') && !has('win32unix') && has('unix')
  let g:ackprg="ack-grep -H --nocolor --nogroup --column"
endif

let g:ctrlp_extensions = ['tag', 'buffertag']
let g:ctrlp_custom_ignore = '\.pyc$'

" Strip tagfiles up to 64MB
let g:autotagmaxTagsFileSize = 1024*1024*64

" Reset cursor to last pos in file
function! ResCur()
  if line("'\"") <= line("$")
    normal! g`"
    return 1
  endif
endfunction

augroup resCur
  autocmd!
  autocmd BufWinEnter * call ResCur()
augroup END

set rtp+=~/.vim

if has('win32')
  " Maximize, baby!
  autocmd GUIEnter * simalt ~X
endif

au! BufRead,BufNewFile *.ninja set filetype=ninja
au! BufWritePost * silent call s:FixExecutable()
function s:FixExecutable()
  if strpart(getline(1), 0, 2) == '#!'
    !chmod +x %
  else
    !chmod -x %
  endif
endfunction

" turn on automatic text wrapping for git commit files.
au FileType gitcommit setlocal fo+=t

au FileType python setlocal ts=2 sts=2 sw=2

au FileType go setlocal listchars=tab:\ \ ,eol:¬,extends:❯,precedes:❮
au FileType go setlocal noexpandtab
au BufWritePre *.go lua vim.lsp.buf.format({ async = false })

if executable('/usr/local/bin/git')
  let g:fugitive_git_executable='/usr/local/bin/git'
endif

function! Banner()
python << EOF
import vim
fchar = "/"
if vim.current.buffer.name.endswith((".py", ".sh")):
  fchar = "#"
cline = vim.current.line.strip().strip(fchar).strip()
vim.current.line = (" %s " % cline).center(80, fchar)
EOF
endfunction

command Banner call Banner()

vmap <silent> R :sort i<cr>

lua <<EOF
  vim.keymap.set("n", "[g", vim.diagnostic.goto_prev)

  local M = {}

  M.pos_equal = function (p1, p2)
    local r1, c1 = unpack(p1)
    local r2, c2 = unpack(p2)
    return r1 == r2 and c1 == c2
  end

  M.goto_error_then_hint = function ()
    local pos = vim.api.nvim_win_get_cursor(0)
    vim.diagnostic.goto_next( {severity=vim.diagnostic.severity.ERROR, wrap = true} )
    local pos2 = vim.api.nvim_win_get_cursor(0)
    if ( M.pos_equal(pos, pos2)) then
      vim.diagnostic.goto_next( {wrap = true} )
    end
  end

  vim.keymap.set("n", "]g", M.goto_error_then_hint)
  vim.keymap.set("n", "]G", vim.diagnostic.goto_next)
EOF

if executable('rg')
	set grepprg=rg\ --vimgrep\ --hidden\ --glob\ '!.git'
endif
