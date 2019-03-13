workflow "On PR" {
  on = "pull_request"
  resolves = ["ansible/ansible-lint-action@master"]
}

action "ansible/ansible-lint-action@master" {
  uses = "ansible/ansible-lint-action@master"
  env = {
    ACTION_PLAYBOOK_NAME = "."
  }
}
