set tabstop=2
set textwidth=80
set shiftwidth=2
set softtabstop=2
set smarttab

" Stop the crazy margins :D
set numberwidth=2

" More useful than not
set ignorecase

" Modelines
set modeline
set modelines=5

set expandtab

set nowrap

set wildmenu
set wildmode=list:longest,full

set tildeop

set foldlevelstart=99

set guifont=DejaVu_Sans_Mono_for_Powerline:h11:cANSI

" For tagbar to update highlighted element faster
set ut=1000

" Search upwards until there's a tags file
set tags+=./tags;

set mouse=a

nunmap ;
nunmap <C-h>
nunmap <C-j>
nunmap <C-k>
nunmap <C-l>

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


" Let's stick with hybrid for now
" colorscheme distinguished
hi! Operator guifg=#cc6666 ctermfg=9 guibg=NONE ctermbg=NONE gui=NONE term=NONE

if !has('mac') && !has('win32unix') && has('unix')
  let g:ackprg="ack-grep -H --nocolor --nogroup --column"
endif

let g:ctrlp_extensions = ['tag', 'buffertag']
let g:ctrlp_custom_ignore = '\.pyc$'

let g:SuperTabDefaultCompletionType = "context"
let g:SuperTabLongestEnhanced = 1
let g:SuperTabLongestHighlight = 1
let g:SuperTabClosePreviewOnPopupClose = 1

" Backwards is effectively '\<\>', but there seems to be a bug in snips...
let g:snips_trigger_key = ",."
let g:snips_trigger_key_backwards = "\<"
let g:snipMate = {}
let g:snipMate.scope_aliases = {}
let g:snipMate.scope_aliases['htmldjango'] = 'htmldjango,xhtml,html,javascript'

let g:syntastic_python_checker = 'pylint'
let g:syntastic_python_checker_args = '--ignore=E111,E128,E121'

let g:pymode_options_indent = 0
let g:pymode_rope = 0

" Let syntastic handle linting
let g:pymode_lint_write = 0

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

filetype on
filetype plugin indent on
au FileType python set ts=2 sts=2 sw=2

if executable('/usr/local/bin/git')
  let g:fugitive_git_executable='/usr/local/bin/git'
endif
