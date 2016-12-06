#!/bin/bash

# Credits:
# https://blog.heckel.xyz/2015/03/24/bash-completion-with-sub-commands-and-dynamic-options/
# https://raw.githubusercontent.com/syncany/syncany/develop/gradle/bash/syncany.bash-completion

shopt -s progcomp

_platforms(){
  molecule status --porcelain --platforms | cut -d' ' -f1 2>/dev/null
}

_providers(){
  molecule status --porcelain --providers | cut -d' ' -f1 2>/dev/null
}

_hosts(){
  molecule status --porcelain --hosts | cut -d' ' -f1 2>/dev/null
}

_molecule(){
  local cur prev firstword lastword complete_words complete_options
  cur=${COMP_WORDS[COMP_CWORD]}
	prev=${COMP_WORDS[COMP_CWORD-1]}
	firstword=$(_get_firstword)

  GLOBAL_COMMANDS="syntax create converge destroy idempotence init list login status test verify"
  GLOBAL_OPTIONS="-h -v"
  SYNTAX_OPTIONS=""
  CHECK_OPTIONS=""
  CREATE_OPTIONS="--debug --platform --provider --tags"
  CONVERGE_OPTIONS="--debug --platform --provider --tags"
  DEPENDENCY_OPTIONS=""
  DESTROY_OPTIONS="--debug --platform --provider --tags"
  IDEMPOTENCE_OPTIONS="--debug --platform --provider --tags"
  INIT_OPTIONS="--docker"
  LIST_OPTIONS="--debug -m"
  LOGIN_OPTIONS=""
  STATUS_OPTIONS="--debug --hosts --platforms --porcelain --providers"
  TEST_OPTIONS="--debug --platform --provider --tags --sudo"
  VERIFY_OPTIONS="--debug --platform --provider --tags --sudo"

  # Un-comment this for debug purposes:
  # echo -e "\nprev = $prev, cur = $cur, firstword = $firstword.\n"

  case "${firstword}" in
    check)
      complete_options="${CHECK_OPTIONS}"
      ;;
    create)
      case "${prev}" in
        --platform)
          complete_words=$(_platforms)
          ;;
        --provider)
          complete_words=$(_providers)
          ;;
        *)
          complete_options="${CREATE_OPTIONS}"
          ;;
      esac
      ;;
    converge)
      case "${prev}" in
        --platform)
          complete_words=$(_platforms)
          ;;
        --provider)
          complete_words=$(_providers)
          ;;
        *)
          complete_options="${CONVERGE_OPTIONS}"
          ;;
      esac
      ;;
    dependency)
      complete_options="${CHECK_OPTIONS}"
      ;;
    destroy)
      case "${prev}" in
        --platform)
          complete_words=$(_platforms)
          ;;
        --provider)
          complete_words=$(_providers)
          ;;
        *)
          complete_options="${DESTROY_OPTIONS}"
          ;;
      esac
      ;;
    idempotence)
      case "${prev}" in
        --platform)
          complete_words=$(_platforms)
          ;;
        --provider)
          complete_words=$(_providers)
          ;;
        *)
          complete_options="${IDEMPOTENCE_OPTIONS}"
          ;;
      esac
      ;;
    init)
      complete_options="${INIT_OPTIONS}"
      ;;
    list)
      complete_options="${LIST_OPTIONS}"
      ;;
    login)
      complete_options="${LOGIN_OPTIONS}"
      complete_words=$(_hosts)
      ;;
    status)
      complete_options="${STATUS_OPTIONS}"
      ;;
    syntax)
      complete_options="${SYNTAX_OPTIONS}"
      ;;
    test)
      case "${prev}" in
        --platform)
          complete_words=$(_platforms)
          ;;
        --provider)
          complete_words=$(_providers)
          ;;
        *)
          complete_options="${TEST_OPTIONS}"
          ;;
      esac
      ;;
    verify)
      case "${prev}" in
        --platform)
          complete_words=$(_platforms)
          ;;
        --provider)
          complete_words=$(_providers)
          ;;
        *)
          complete_options="${VERIFY_OPTIONS}"
          ;;
      esac
      ;;
    *)
  		complete_words="${GLOBAL_COMMANDS}"
  		complete_options="${GLOBAL_OPTIONS}"
  		;;
  esac

  # Either display words or options, depending on the user input
	if [[ ${cur} == -* ]]; then
		COMPREPLY=( $( compgen -W "${complete_options}" -- ${cur} ))
	else
		COMPREPLY=( $( compgen -W "${complete_words}" -- ${cur} ))
	fi

	return 0
}

# Determines the first non-option word of the command line. This is usually the command.
_get_firstword() {
	local firstword i

	firstword=
	for ((i = 1; i < ${#COMP_WORDS[@]}; ++i)); do
		if [[ ${COMP_WORDS[i]} != -* ]]; then
			firstword=${COMP_WORDS[i]}
			break
		fi
	done

	echo $firstword
}

complete -F _molecule molecule
