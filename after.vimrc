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

" Undo Space to toggle folds, because it screws with Ack.vim.
nunmap <Enter>
vunmap <Enter>

colorscheme molokai 

let g:ackprg="ack-grep -H --nocolor --nogroup --column"

let g:ctrlp_extensions = ['tag', 'buffertag']

let g:SuperTabDefaultCompletionType = "context"
let g:SuperTabContextDefaultCompletionType = "<c-x><c-o>"
let g:SuperTabLongestEnhanced = 1
let g:SuperTabLongestHighlight = 1
let g:SuperTabClosePreviewOnPopupClose = 1

" Go find first django_project and do the omnidance :)
let s:proj_file=findfile(".django_project", ';')
if !empty(s:proj_file)
  let $DJANGO_SETTINGS_MODULE=readfile(s:proj_file)[0]
  python "sys.path.append(os.getcwd())"
endif

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
