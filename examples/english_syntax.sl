// ScratchLang 英文语法示例
// English syntax example

#Player

var: score = 0
var: speed = 5
cloud: highscore = 0

when flag clicked
    go to x: 0 y: 0
    set size to 100
    say "Welcome! Use arrow keys to move" 2 seconds

when up key pressed
    change y by ~speed

when down key pressed
    change y by -5

when left key pressed
    change x by -5

when right key pressed
    change x by ~speed

when space key pressed
    change score by 1
    say ~score

// Custom block definition
define moveAndSay(steps, message)
    move ~steps steps
    say ~message
end

// Custom block with warp mode
define fastCalculate(times) warp
    repeat ~times
        change score by 1
    end
end

when this sprite clicked
    moveAndSay 10 "Hello!"
    fastCalculate 100
