" vimrc
" Author: Robbie Iannucci <robbie@rail.com>
" Source: https://github.com/riannucci/vimified
" Original Author: Zaiste! <oh@zaiste.net>
" Original Source: https://github.com/zaiste/vimified
"
" Have fun!
"

set nocompatible
filetype off

let mapleader = ","
let maplocalleader = "\\"

set rtp+=~/.vim/bundle/vundle/
call vundle#rc()

Bundle 'gmarik/vundle'

if !has('win32')
  if filereadable(expand('~/.at_work'))
    source ~/.vimrc_at_work
  else
    Bundle 'Valloric/YouCompleteMe'
  endif
  nnoremap <silent><space> :YcmCompleter GoToDefinitionElseDeclaration<cr>
endif

Bundle "bronson/vim-visual-star-search"

Bundle "SirVer/ultisnips"
Bundle "honza/vim-snippets"
let g:UltiSnipsExpandTrigger="<leader>."
let g:UltiSnipsJumpForwardTrigger="<leader>."

Bundle "airblade/vim-gitgutter"

Bundle "ehamberg/vim-cute-python"

Bundle 'bling/vim-airline'
if !exists('g:airline_symbols')
  let g:airline_symbols = {}
endif
let g:airline_left_sep = ''
let g:airline_left_alt_sep = ''
let g:airline_right_sep = ''
let g:airline_right_alt_sep = ''
let g:airline_symbols.branch = ''
let g:airline_symbols.readonly = ''
let g:airline_symbols.linenr = ''
let g:airline_symbols.whitespace = 'Ξ'

Bundle 'goldfeld/vim-seek'
let g:seek_subst_disable = 1

Bundle 'vim-scripts/Align'
Bundle 'tpope/vim-endwise'
Bundle 'tpope/vim-repeat'
Bundle 'tpope/vim-speeddating'
Bundle 'tpope/vim-surround'
Bundle 'tpope/vim-unimpaired'

Bundle 'kien/ctrlp.vim'

Bundle 'majutsushi/tagbar'
nmap <leader>t :TagbarToggle<CR>

Bundle 'tpope/vim-fugitive'

Bundle 'scrooloose/syntastic'
let g:syntastic_aggregate_errors = 1
let g:syntastic_always_populate_loc_list=1
let g:syntastic_auto_loc_list=1
let g:syntastic_enable_signs=1
let g:syntastic_error_symbol = "✗"
let g:syntastic_go_checkers = ['go', 'govet', 'golint']
let g:syntastic_loc_list_height=5
let g:syntastic_warning_symbol = "⚠"

Bundle 'hynek/vim-python-pep8-indent'

Bundle 'Raimondi/delimitMate'
let g:delimitMate_expand_space = 1
let g:delimitMate_expand_cr = 1

autocmd FileType gitcommit set tw=68 spell

Bundle 'w0ng/vim-hybrid'

Bundle 'kchmck/vim-coffee-script'

Bundle 'fatih/vim-go'
let g:go_fmt_options = '-s=true -e=true'

filetype plugin indent on
set background=dark
colorscheme hybrid
syntax on

hi SyntasticErrorSign ctermfg=160
hi SyntasticWarningSign ctermfg=221

" Set 5 lines to the cursor - when moving vertically
set scrolloff=5

" Highlight VCS conflict markers
match ErrorMsg '^\(<\|=\|>\)\{7\}\([^=].\+\)\?$'

" clear highlight after search
noremap <silent><leader>/ :nohls<CR>

" Emacs bindings in command line mode
cnoremap <c-a> <home>
cnoremap <c-e> <end>


set autoread
set backspace=indent,eol,start
set cinoptions=:0,(s,u0,U1,g0,t0
set completeopt=menuone,preview
set encoding=utf-8
set hidden
set history=1000
set incsearch
set laststatus=2
set list

" Don't redraw while executing macros
set nolazyredraw

" Disable the macvim toolbar
set guioptions-=T

set listchars=tab:▸\ ,eol:¬,extends:❯,precedes:❮,trail:␣
set showbreak=↪

set notimeout
set ttimeout
set ttimeoutlen=10

" _ backups {{{
set undodir=~/.vim/tmp/undo//     " undo files
set backupdir=~/.vim/tmp/backup// " backups
set directory=~/.vim/tmp/swap//   " swap files
set backup
set noswapfile
" _ }}}

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

set completeopt=longest,menuone,preview

set autoindent
set formatoptions=qrn1
let &colorcolumn="+1,".join(range(120,320), ",")

set visualbell


set dictionary=/usr/share/dict/words

set tabstop=2
set textwidth=80
set shiftwidth=2
set softtabstop=2
set smarttab

" Stop the crazy margins :D
set numberwidth=2

" Modelines
set modeline
set modelines=5

set expandtab

set nowrap

set wildmenu
set wildignore=.svn,CVS,.git,.hg,*.o,*.a,*.class,*.mo,*.la,*.so,*.obj,*.swp,*.jpg,*.png,*.xpm,*.gif,.DS_Store,*.aux,*.out,*.toc
set wildmode=list:longest,full

set tildeop

set foldlevelstart=99

set guifont=DejaVu_Sans_Mono_for_Powerline:h11:cANSI

" For tagbar to update highlighted element faster
set ut=1000

" Search upwards until there's a tags file
set tags+=./tags;

set mouse=a

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
set hlsearch

" Don't jump when using * for search
nnoremap * *<c-o>

" Keep search matches in the middle of the window.
nnoremap n nzzzv
nnoremap N Nzzzv

" Same when jumping around
nnoremap g; g;zz
nnoremap g, g,zz

" Open a Quickfix window for the last search.
nnoremap <silent> <leader>? :execute 'vimgrep /'.@/.'/g %'<CR>:copen<CR>

" Highlight word {{{

nnoremap <silent> <leader>hh :execute 'match InterestingWord1 /\<<c-r><c-w>\>/'<cr>
nnoremap <silent> <leader>h1 :execute 'match InterestingWord1 /\<<c-r><c-w>\>/'<cr>
nnoremap <silent> <leader>h2 :execute '2match InterestingWord2 /\<<c-r><c-w>\>/'<cr>
nnoremap <silent> <leader>h3 :execute '3match InterestingWord3 /\<<c-r><c-w>\>/'<cr>

" }}}

" }}}

set foldmethod=syntax

" Make zO recursively open whatever top level fold we're in, no matter where the
" cursor happens to be.
nnoremap zO zCzO

" Use ,z to "focus" the current fold.
nnoremap <leader>z zMzvzz

function! MyFoldText()
    let line = getline(v:foldstart)

    let nucolwidth = &fdc + &number * &numberwidth
    let windowwidth = winwidth(0) - nucolwidth - 3
    let foldedlinecount = v:foldend - v:foldstart

    " expand tabs into spaces
    let onetab = strpart('          ', 0, &tabstop)
    let line = substitute(line, '\t', onetab, 'g')

    let line = strpart(line, 0, windowwidth - 2 -len(foldedlinecount))
    let fillcharcount = windowwidth - len(line) - len(foldedlinecount)
    return line . '…' . repeat(" ",fillcharcount) . foldedlinecount . '…' . ' '
  endfunction
set foldtext=MyFoldText()

" _ Vim {{{
augroup ft_vim
    au!

    au FileType vim setlocal foldmethod=marker
    au FileType help setlocal textwidth=78
    au BufWinEnter *.txt if &ft == 'help' | wincmd L | endif
augroup END


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

" Display an error message.
function! s:Warn(msg)
  echohl ErrorMsg
  echomsg a:msg
  echohl NONE
endfunction

" Command ':Bclose' executes ':bd' to delete buffer in current window.
" The window will show the alternate buffer (Ctrl-^) if it exists,
" or the previous buffer (:bp), or a blank buffer if no previous.
" Command ':Bclose!' is the same, but executes ':bd!' (discard changes).
" An optional argument can specify which buffer to close (name or number).
function! s:Bclose(bang, buffer)
  if empty(a:buffer)
    let btarget = bufnr('%')
  elseif a:buffer =~ '^\d\+$'
    let btarget = bufnr(str2nr(a:buffer))
  else
    let btarget = bufnr(a:buffer)
  endif
  if btarget < 0
    call s:Warn('No matching buffer for '.a:buffer)
    return
  endif
  if empty(a:bang) && getbufvar(btarget, '&modified')
    call s:Warn('No write since last change for buffer '.btarget.' (use :Bclose!)')
    return
  endif
  " Numbers of windows that view target buffer which we will delete.
  let wnums = filter(range(1, winnr('$')), 'winbufnr(v:val) == btarget')
  if !g:bclose_multiple && len(wnums) > 1
    call s:Warn('Buffer is in multiple windows (use ":let bclose_multiple=1")')
    return
  endif
  let wcurrent = winnr()
  for w in wnums
    execute w.'wincmd w'
    let prevbuf = bufnr('#')
    if prevbuf > 0 && buflisted(prevbuf) && prevbuf != w
      buffer #
    else
      bprevious
    endif
    if btarget == bufnr('%')
      " Numbers of listed buffers which are not the target to be deleted.
      let blisted = filter(range(1, bufnr('$')), 'buflisted(v:val) && v:val != btarget')
      " Listed, not target, and not displayed.
      let bhidden = filter(copy(blisted), 'bufwinnr(v:val) < 0')
      " Take the first buffer, if any (could be more intelligent).
      let bjump = (bhidden + blisted + [-1])[0]
      if bjump > 0
        execute 'buffer '.bjump
      else
        execute 'enew'.a:bang
      endif
    endif
  endfor
  execute 'bdelete'.a:bang.' '.btarget
  execute wcurrent.'wincmd w'
endfunction
command! -bang -complete=buffer -nargs=? Bclose call s:Bclose('<bang>', '<args>')
nnoremap <silent> <Leader>bd :Bclose<CR>


" Tagbar mapping interferes with Align
nunmap <Leader>t
nmap   <Leader>, :TagbarToggle<CR>
let g:tagbar_autoclose=1


" Shift-arrows work like you would kinda expect them to :)
imap <S-Up>    <esc>v<Up>
imap <S-Down>  <esc>v<Down>
imap <S-Left>  <esc>v<Left>
imap <S-Right> <esc>v<Right>
nmap <S-Up>    v<Up>
nmap <S-Down>  v<Down>
nmap <S-Left>  v<Left>
nmap <S-Right> v<Right>
vmap <S-Up>    <Up>
vmap <S-Down>  <Down>
vmap <S-Left>  <Left>
vmap <S-Right> <Right>

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

" Go find first django_project and do the omnidance :)
let s:proj_file=findfile(".django_project", ';')
if !empty(s:proj_file)
  let $DJANGO_SETTINGS_MODULE=readfile(s:proj_file)[0]
  python "sys.path.append(os.getcwd())"
endif

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

" auto-close the python preview pane
autocmd InsertLeave * if pumvisible() == 0|pclose|endif

for f in split(glob('~/.vim/syntax_checkers/*.vim'), '\n')
      exe 'source' f
endfor

set rtp+=~/.vim

if has('win32')
  " Maximize, baby!
  autocmd GUIEnter * simalt ~X
endif

au! BufRead,BufNewFile *.ninja set filetype=ninja
au! BufWritePost *.py,*.sh silent call s:FixExecutable()
function s:FixExecutable()
  if strpart(getline(1), 0, 2) == '#!'
    !chmod +x %
  else
    !chmod -x %
  endif
endfunction

au FileType python setlocal ts=2 sts=2 sw=2
au FileType go setlocal listchars=tab:\ \ ,eol:¬,extends:❯,precedes:❮,trail:␣
au FileType go setlocal noexpandtab

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
