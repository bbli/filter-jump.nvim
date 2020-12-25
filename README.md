filter-jump
==========
## Motivation
I wanted a smooth way to move the cursor subject to certain criterion in the follow scenarios:
1. Large Screen Wide Movement:
    * No typing numbers: As explained in this [video](https://www.youtube.com/watch?v=tSq7yDwS1vM&list=LLfDw9928RXloc-CAvO-h-Kw&index=368), numbers are far away and do not keep your typing "cache-friendly".(Also I'm just bad at touch typing numbers)
    * Jump actually adds to jumps list: For example, relative movements(i.e `10j`) will not be added to the jumplist. Although absolute movements do add to the jumplist, this may force you to type 3+ numbers, which as explained above, is slowww.
2. Better One Line `f` Functionality:
    * Vim's normal mode `f` suffers from two main problems . First, often times one character is just too imprecise, which will means we have to traverse with `;` 2-4 times before reaching our destination. 
    * Second, because the matching results are not highlighted, it is hard to know exactly how many times we have to press `;`. To continue with our computer science analogy, we are basically traversing at the speed of a linked list, where we are unable to "prefetch" the next memory segment(aka whether or not to change the character we are searching for or just keep spamming `;`) until we have arrived at the current node(aka match).

Furthermore, the following plugins could not produce the behavior I wanted, for various reasons:
* [EasyMotion](https://github.com/easymotion/vim-easymotion): Causes too much screen bloat/color change + typing of "random" characters. Personally I rather type more characters but have them actually be words in my current document, as this keeps my brain more "in the flow"
* [Vim-Sneak](https://github.com/justinmk/vim-sneak): Highlighting all possible matches is good as it solves my second issue with `f` mentioned above. But doesn't provide me the option of only searching the current line, as I feel that two characters will often have too many results when searching the entire page, and so that's where something like `/` would be better
* [Aerojump](https://github.com/ripxorip/aerojump.nvim): This plugin was probably the closest thing that fit my needs for screen wide movements, except too many results/screen bloat would appear as a result of the fuzzy matching.
* Built in `/`: On the flip side, `/` forces me to type the word exactly as is, whereas most of the time I didn't care for typing out characters such as underscores. Also `/` searches the entire file, whereas I just want to jump to a location in the current window view. This is suboptimal for when `/` does find a match out of screen, as my screen will "move", which I don't want. Finally, this pollutes my search history, which is important for my workflow since I mapped `/` to fzf's Search History finder.

And finally, because I wanted an excuse to write my first Vim plugin :). So perhaps the behavior I wanted could have been achieved through advanced configuration/hacking of the above plugins.


## Installation
Use your favorite plugin manager, such as [vim-plug](https://github.com/junegunn/vim-plug):
```
Plug 'bbli/filter-jump.nvim', {'do': ':UpdateRemotePlugins'}
```
## Mappings/Usage
### Examples
* All words/characters after the initial one will be used to "filter" the matches. My idea was basically to keep typing words/phrases around the place I want to jump to rather than do something that involved more "decision making", such as planning a sequence of vim motions or thinking about the least commonly occuring characters.
![filter](imgs/filter.svg)

* Or you can just start moving to the next matches.If result is near bottom, I just use `<C-p>` instead
![select_next](imgs/select_next_match.svg)

* Or do both! The algorithm will keep track of where your latest selection is at and will choose the closest among the new set of highlights
![find_closet](imgs/find_closet.svg)

* Finally, you can call `FilterJumpLineForward` and `FilterJumpLineBackward` for variable length `f/F` search. Note that all options from above are available in this mode too, though I doubt you need them
![one_line](imgs/one_line.svg)

### HOW TO
1. Opening FilterJump
* Add a map to `<Plug>(FilterJump)` in your vimrc. This also exists as a command mode command `:FilterJump`.(There is no default mapping)
```
nmap s <Plug>(FilterJump)
```
2. FilterJump Action Keys
* These are the default hotkeys. Add this to your vimrc and change it if you want
* You can also call the built in Vim command `:bwipeout` or `:bdelete` while in normal mode within the jump buffer, and the buffer and highlights will also be cleared.
```
let g:filter_jump_keymaps = {
    \ "<C-n>" : "FilterJumpNextMatch",
    \ "<C-p>" "FilterJumpPrevMatch",
    \ "<CR>" : "FilterJumpSelect",
    \ "<C-f>" : "FilterJumpSelect",
    \ "<C-c>" : "FilterJumpExit" "Note this one overrides the default Vim command, which goes back to normal mode
    \}
```

## More Customization
### Characters to Ignore
By default, this plugin will just ignore `_` when searching. To override this:
```
let g:filter_jump_strip_characters = ["_","@"]
```
### Setting specific options in the JumpBuffer
* Since the search word is typed in a temporary buffer, there may be some keymaps that you would like to not be triggered in this buffer.(As shown below, you actually can put any command mode command into the list, and they will be called when the JumpBuffer is opened) 
```
let g:filter_jump_buffer_options = ["inoremap <buffer> <C-j> <Nop>","CocDisable"]
```
### Changing the Highlight Coloring
This plugin defines the highlight groups `SearchCurrent` and `SearchHighlights`, and maps them to built in `Search` and `IncSearch` highlight groups respectively. If you would like to change that, add something like the following:
```
highlight! link SearchCurrent Red "This assumes you have the Red highlight group defined.
highlight! link SearchHighlights Green
```
## Acknowledgements
[Aerojump](https://github.com/ripxorip/aerojump.nvim) for the settings I need to set when opening the jump buffer and keymapping code
