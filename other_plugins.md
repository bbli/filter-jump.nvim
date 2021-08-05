* [EasyMotion](https://github.com/easymotion/vim-easymotion):
    * Causes too much screen bloat/color change + typing of "random" characters. Personally I rather type more characters but have them actually be words in my current document, as this causes less of a "context switch"
* [Vim-Sneak](https://github.com/justinmk/vim-sneak):
    * Highlighting all possible matches is good as it solves my second issue with vim's built in `f` as mentioned in the README. But doesn't provide me the option of only searching the current line, as I feel that two characters will often have too many results when searching the entire page, and so that's where something like `/` would be better
    * While sneak provides a function that you can use to search using more than two characters -> this has the downside of not being incremental: in that you need to wait longer for results to start popping up on your screen -> so you don't have the ability to "branch predict"
    * Furthermore, because you only type 2/fixed amount of characters -> you have to consciously "decelerate" your typing, which puts a limiter on how fast you can type+you don't get to choose when you context switch from typing to selection
* [Aerojump](https://github.com/ripxorip/aerojump.nvim):
    * This plugin was probably the closest thing that fit my needs for screen wide movements, except too many results/screen bloat would appear as a result of the fuzzy matching. There are also a couple of "rough" edges about this plugin(TODO: explain)
