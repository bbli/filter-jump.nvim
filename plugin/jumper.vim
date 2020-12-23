nnoremap <silent> <Plug>(FilterJumpOpen) :FilterJumpOpen<Return>

if !exists("g:filter_jump_highlight_groups")
    highlight! link SearchCurrent Search
    highlight! link SearchHighlights Visual
endif

