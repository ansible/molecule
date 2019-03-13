workflow "On PR" {
  on = "pull_request"
  resolves = ["Run Ansible Lint"]
}

action "Run Ansible Lint" {
  uses = "ansible/ansible-lint-action@master"
  env = {
    ACTION_PLAYBOOK_NAME = "."
  }
}
