# Commands

Commands are a convenient way to operate `vibe` without restarting it and rewriting configs.

All commands follow this syntax:

```
/<command> <args>
```
Some commands change session-wide settings, while others can change [persistent settings](config.md)

## model
```
/model
```

Switch a model

Prints current model and takes new model name.
If no input provided (user just pressed Enter without typing anything) then nothing changes.

## hist
```
/hist
```

Display conversation history.

Prints current loaded conversation including prompts, responses and tool calls.

## histpop
```
/histpop
```
Remove last entry from history 

## redo
```
/redo
```
Run LLM request with [current history](#hist) (as it is, without any additions) as input.

Useful in cases when something crashed and you need to rerun last request 