
if !exists('g:syntastic_cpp_linter')
  let g:syntastic_cpp_linter = 'cpplint.bat'
endif

if !executable(g:syntastic_cpp_linter)
  echo "Linter isn't executable!"
  finish
endif

let g:loaded_cpp_syntax_checker = 1

function! SyntaxCheckers_cpp_GetLocList()
  let makeprg  = g:syntastic_cpp_linter . ' --output=emacs --filter=+ '
  let makeprg .= shellescape(expand('%'))
  let errorformat = "%f:%l:  %m"

  " process makeprg
  return SyntasticMake({ 'makeprg': makeprg,
              \ 'errorformat': errorformat })
endfunction
