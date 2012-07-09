set tabstop=2 
set textwidth=90
set shiftwidth=2 
set softtabstop=2

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

" Undo Space to toggle folds, because it screws with Ack.vim.
nunmap <Enter>
vunmap <Enter>

colorscheme molokai 

if !has('mac') && has('unix')
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
