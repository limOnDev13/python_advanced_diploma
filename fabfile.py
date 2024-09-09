from fabric import task, Connection


@task
def deploy(ctx):
    with Connection(
        "10.130.0.32",
        user="volosnikovvs",
        connect_kwargs={"key_filename": "./sshkeys/yandexcloud"}
    ) as c:
        with c.cd("/home/ec2-user/automated-deployment"):
            c.run("docker compose down")
            c.run("git pull origin master --rebase")
            c.run("docker compose build")
            c.run("docker compose up")

