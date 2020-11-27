let g:animal = 'cat'
echo 'about to print'
echo g:animal

let index = 0
while index < 2
    echo 'hi'
    let index = index + 1
endwhile

if filereadable(expand('%'))
    echom 'Current file (' . expand('%:t') . ') is readable!'
endif
function g:Mynumber(arg)
  echo line(".") . " " . a:arg
endfunction

function! GetPotionFold(lnum)
    if getline(a:lnum) =~? '\v^\s*$'
        return '-1'
    endif

    return '0'
endfunction
"1,5call Mynumber(getline("."))

