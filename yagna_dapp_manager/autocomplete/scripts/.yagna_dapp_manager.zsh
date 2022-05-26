
#compdef yagna_dapp_manager

_yagna_dapp_manager_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[yagna_dapp_manager] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _YAGNA_DAPP_MANAGER_COMPLETE=zsh_complete yagna_dapp_manager)}")

    for type key descr in ${response}; do
        if [[ "$type" == "plain" ]]; then
            if [[ "$descr" == "_" ]]; then
                completions+=("$key")
            else
                completions_with_descriptions+=("$key":"$descr")
            fi
        elif [[ "$type" == "dir" ]]; then
            _path_files -/
        elif [[ "$type" == "file" ]]; then
            _path_files -f
        fi
    done

    if [ -n "$completions_with_descriptions" ]; then
        _describe -V unsorted completions_with_descriptions -U
    fi

    if [ -n "$completions" ]; then
        compadd -U -V unsorted -a completions
    fi
}

compdef _yagna_dapp_manager_completion yagna_dapp_manager;

