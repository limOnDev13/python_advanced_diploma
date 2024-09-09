import os

from fabric import Connection, task


@task
def deploy(ctx):
    with Connection(
        os.environ["EC2_HOST"],
        user=os.environ["EC2_USER"],
        connect_kwargs={"key_filename": os.environ["EC2_PRIVATE_KEY"]}
    ) as c:
        with c.cd("/src"):
            c.run("docker compose down")
            c.run("echo 'After docker compose down'")
            c.run("git pull origin master --recurse-submodules --rebase")
            c.run("echo 'After pull'")
            c.run("docker compose build")
            c.run("echo 'After docker compose build'")
            c.run("docker compose up")

