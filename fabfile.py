import os

from fabric import Connection, task


@task
def deploy(ctx):
    with Connection(
        os.environ["EC2_HOST"],
        user=os.environ["EC2_USER"],
        connect_kwargs={"pkey": os.environ["EC2_PRIVATE_KEY"]}
    ) as c:
        with c.cd("python_advanced_diploma"):
            c.run("echo 1")
            c.run('eval "$(ssh-agent -s)"')
            c.run("echo 1.1")
            c.run("ssh-add ~/.sshkeys/gitlab")
            c.run("echo 1.2")
            c.run("docker compose down")
            c.run("echo 2")
            c.run("git pull origin master --recurse-submodules --rebase")
            c.run("echo 3")
            c.run("docker compose build")
            c.run("echo 4")
            c.run("docker compose up")
