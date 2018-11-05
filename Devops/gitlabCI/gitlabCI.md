# docker + gitlab + gitlab-runner 实现 CI

---
版本说明:
 * centos: 7.5（虚拟机）
 * docker: 18.06.1-ce
 * gitlab-ce: 11.3.0
 * gitlab-runner: 11.3.1

## 安装

docker 安装 gitlab-ce 和 gitlab-runner
```sh
docker pull gitlab/gitlab-ce
docker pull gitlab/gitlab-runner
```
## 准备
1.安装 docker
2.新建用户 gitlab，并切换到 gitlab 用户
```sh
useradd -m gitlab
sh -c 'echo xxxxxxxx | passwd gitlab --stdin'
gpasswd -a gitlab root # 把当前用户加进 root 用户组，拥有使用 docker 权限
su gitlab
cd 
mkdir dockerVolume
```

## gitlab 启动及初始化工程

1.启动 gitlab-ce
```sh
sudo docker run --detach \
    --hostname gitlab.example.com \
    --publish 4430:443 --publish 80:80 --publish 2200:22 \
    --name gitlab \
    --restart always \
    --volume /home/gitlab/dockerVolume/gitlab/config:/etc/gitlab \
    --volume /home/gitlab/dockerVolume/gitlab/logs:/var/log/gitlab \
    --volume /home/gitlab/dockerVolume/gitlab/data:/var/opt/gitlab \
    gitlab/gitlab-ce:latest

# gitlab 启动参数说明
#   volume 挂在数据
#   restart 每次 docker 重启都会启动该容器
#   name 命名容器名字
#   hostname 容器域名
```
2.修改配置
修改/root/dockerVolume/gitlab/config/gitlab.rb文件
将
 external_url 值
修改为
 http://宿主机ip
![](external_url.png)

将
gitlab_rails['gitlab_shell_ssh_port'] =
值修改为 2200
![](ssh_port.png)
3.重启镜像
```sh
docker restart gitlab
```

4.注册 gitlab 用户
当 gitlab 容器启动成功后，浏览器打开`宿主机ip:8000`,填写 root 用户密码。
![](root_login.png)
密码输入后点击`change you password`，页面跳转到登陆页面

先不慌登陆，我们再注册一个新用户`superbear`

输入用户名和密码，用户名为`root`,密码为刚才输入的密码，点击`sign in`，登陆成功后页面如下:
![](index.png)

点击`create a group`创建一个新的用户组，填写用户组信息
![](base_group.png)
将刚才创建的账号`superbear`添加到`base`用户组，角色设置为`Owner`
![](add_superbear.png)
5.退出`root`用户，登陆`superbear`用户

6.创建一个名称为`test`新的工程，并创建一个新分支`develop`,修改默认分支为`develop`
![](new_project.png)

## gitlab-runner 启动及配置
1.启动 gitlab-runer
```sh
sudo docker run -d --name gitlab-runner --restart always \
  -v /home/gitlab/dockerVolume/gitlab-runner/config:/etc/gitlab-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitlab/gitlab-runner:latest
```

2.注册 gitlab-runner
```sh
sudo docker exec -it gitlab-runner gitlab-ci-multi-runner register
```
配置对应信息如下：
```
Please enter the gitlab-ci coordinator URL -> http://192.168.16.16:8000,
Please enter the gitlab-ci token for this runner -> kTMZyFsVf4DMy5gayWqy,
Please enter the gitlab-ci description for this runner -> test-runner,
Please enter the gitlab-ci tags for this runner (comma separated) -> superbear,
Please enter the executor: parallels, ssh, kubernetes, docker, docker-ssh, shell, virtualbox, docker+machine, docker-ssh+machine -> docker,
Please enter the default Docker image (e.g. ruby:2.1) -> node
```
上面配置信息中`Please enter the gitlab-ci coordinator URL`和`Please enter the gitlab-ci coordinator URL`字段信息来自与 gitlab 的 test 工程信息中
![](gitlab-runner_config.png)

配置成功后刷新 test 工程的 CI/CD页面，可以看见gitlab-runner 配置成功的信息
![](gitlab-runner_success.png)

修改 runner 配置，让 runner 能够执行没有 tag 的 job
![](modify_runner.png)

## 修改代码
1.拉取 test 工程到本地
```
git clone ssh://git@192.168.16.16:2200/superbear/test.git
```
2.修改代码
目录如下
```
├── index.js
├── package.json
├── package-lock.json
├── .gitlab-ci.yml
├── .gitignore
└── README.md
```
代码内容如下
```js
// index.js
const express = require('express')
const app = express()
const port = 3000

app.get('/', (req, res) => res.send('Hello World!'))

app.listen(port, () => console.log(`Example app listening on port ${port}!`))
```
```json
// package.json
{
  "name": "test",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "repository": {
    "type": "git",
    "url": "ssh://git@192.168.16.16:2200/superbear/test.git"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "dependencies": {
    "express": "^4.16.3"
  }
}
```
```json
// package-lock.json
{
  "name": "test",
  "version": "1.0.0",
  "lockfileVersion": 1,
  "requires": true,
  "dependencies": {
    "accepts": {
      "version": "1.3.5",
      "resolved": "http://registry.npm.taobao.org/accepts/download/accepts-1.3.5.tgz",
      "integrity": "sha1-63d99gEXI6OxTopywIBcjoZ0a9I=",
      "requires": {
        "mime-types": "~2.1.18",
        "negotiator": "0.6.1"
      }
    },
    "array-flatten": {
      "version": "1.1.1",
      "resolved": "http://registry.npm.taobao.org/array-flatten/download/array-flatten-1.1.1.tgz",
      "integrity": "sha1-ml9pkFGx5wczKPKgCJaLZOopVdI="
    },
    "body-parser": {
      "version": "1.18.2",
      "resolved": "http://registry.npm.taobao.org/body-parser/download/body-parser-1.18.2.tgz",
      "integrity": "sha1-h2eKGdhLR9hZuDGZvVm84iKxBFQ=",
      "requires": {
        "bytes": "3.0.0",
        "content-type": "~1.0.4",
        "debug": "2.6.9",
        "depd": "~1.1.1",
        "http-errors": "~1.6.2",
        "iconv-lite": "0.4.19",
        "on-finished": "~2.3.0",
        "qs": "6.5.1",
        "raw-body": "2.3.2",
        "type-is": "~1.6.15"
      }
    },
    "bytes": {
      "version": "3.0.0",
      "resolved": "http://registry.npm.taobao.org/bytes/download/bytes-3.0.0.tgz",
      "integrity": "sha1-0ygVQE1olpn4Wk6k+odV3ROpYEg="
    },
    "content-disposition": {
      "version": "0.5.2",
      "resolved": "http://registry.npm.taobao.org/content-disposition/download/content-disposition-0.5.2.tgz",
      "integrity": "sha1-DPaLud318r55YcOoUXjLhdunjLQ="
    },
    "content-type": {
      "version": "1.0.4",
      "resolved": "http://registry.npm.taobao.org/content-type/download/content-type-1.0.4.tgz",
      "integrity": "sha1-4TjMdeBAxyexlm/l5fjJruJW/js="
    },
    "cookie": {
      "version": "0.3.1",
      "resolved": "http://registry.npm.taobao.org/cookie/download/cookie-0.3.1.tgz",
      "integrity": "sha1-5+Ch+e9DtMi6klxcWpboBtFoc7s="
    },
    "cookie-signature": {
      "version": "1.0.6",
      "resolved": "http://registry.npm.taobao.org/cookie-signature/download/cookie-signature-1.0.6.tgz",
      "integrity": "sha1-4wOogrNCzD7oylE6eZmXNNqzriw="
    },
    "debug": {
      "version": "2.6.9",
      "resolved": "http://registry.npm.taobao.org/debug/download/debug-2.6.9.tgz",
      "integrity": "sha1-XRKFFd8TT/Mn6QpMk/Tgd6U2NB8=",
      "requires": {
        "ms": "2.0.0"
      }
    },
    "depd": {
      "version": "1.1.2",
      "resolved": "http://registry.npm.taobao.org/depd/download/depd-1.1.2.tgz",
      "integrity": "sha1-m81S4UwJd2PnSbJ0xDRu0uVgtak="
    },
    "destroy": {
      "version": "1.0.4",
      "resolved": "http://registry.npm.taobao.org/destroy/download/destroy-1.0.4.tgz",
      "integrity": "sha1-l4hXRCxEdJ5CBmE+N5RiBYJqvYA="
    },
    "ee-first": {
      "version": "1.1.1",
      "resolved": "http://registry.npm.taobao.org/ee-first/download/ee-first-1.1.1.tgz",
      "integrity": "sha1-WQxhFWsK4vTwJVcyoViyZrxWsh0="
    },
    "encodeurl": {
      "version": "1.0.2",
      "resolved": "http://registry.npm.taobao.org/encodeurl/download/encodeurl-1.0.2.tgz",
      "integrity": "sha1-rT/0yG7C0CkyL1oCw6mmBslbP1k="
    },
    "escape-html": {
      "version": "1.0.3",
      "resolved": "http://registry.npm.taobao.org/escape-html/download/escape-html-1.0.3.tgz",
      "integrity": "sha1-Aljq5NPQwJdN4cFpGI7wBR0dGYg="
    },
    "etag": {
      "version": "1.8.1",
      "resolved": "http://registry.npm.taobao.org/etag/download/etag-1.8.1.tgz",
      "integrity": "sha1-Qa4u62XvpiJorr/qg6x9eSmbCIc="
    },
    "express": {
      "version": "4.16.3",
      "resolved": "http://registry.npm.taobao.org/express/download/express-4.16.3.tgz",
      "integrity": "sha1-avilAjUNsyRuzEvs9rWjTSL37VM=",
      "requires": {
        "accepts": "~1.3.5",
        "array-flatten": "1.1.1",
        "body-parser": "1.18.2",
        "content-disposition": "0.5.2",
        "content-type": "~1.0.4",
        "cookie": "0.3.1",
        "cookie-signature": "1.0.6",
        "debug": "2.6.9",
        "depd": "~1.1.2",
        "encodeurl": "~1.0.2",
        "escape-html": "~1.0.3",
        "etag": "~1.8.1",
        "finalhandler": "1.1.1",
        "fresh": "0.5.2",
        "merge-descriptors": "1.0.1",
        "methods": "~1.1.2",
        "on-finished": "~2.3.0",
        "parseurl": "~1.3.2",
        "path-to-regexp": "0.1.7",
        "proxy-addr": "~2.0.3",
        "qs": "6.5.1",
        "range-parser": "~1.2.0",
        "safe-buffer": "5.1.1",
        "send": "0.16.2",
        "serve-static": "1.13.2",
        "setprototypeof": "1.1.0",
        "statuses": "~1.4.0",
        "type-is": "~1.6.16",
        "utils-merge": "1.0.1",
        "vary": "~1.1.2"
      }
    },
    "finalhandler": {
      "version": "1.1.1",
      "resolved": "http://registry.npm.taobao.org/finalhandler/download/finalhandler-1.1.1.tgz",
      "integrity": "sha1-7r9O2EAHnIP0JJA4ydcDAIMBsQU=",
      "requires": {
        "debug": "2.6.9",
        "encodeurl": "~1.0.2",
        "escape-html": "~1.0.3",
        "on-finished": "~2.3.0",
        "parseurl": "~1.3.2",
        "statuses": "~1.4.0",
        "unpipe": "~1.0.0"
      }
    },
    "forwarded": {
      "version": "0.1.2",
      "resolved": "http://registry.npm.taobao.org/forwarded/download/forwarded-0.1.2.tgz",
      "integrity": "sha1-mMI9qxF1ZXuMBXPozszZGw/xjIQ="
    },
    "fresh": {
      "version": "0.5.2",
      "resolved": "http://registry.npm.taobao.org/fresh/download/fresh-0.5.2.tgz",
      "integrity": "sha1-PYyt2Q2XZWn6g1qx+OSyOhBWBac="
    },
    "http-errors": {
      "version": "1.6.3",
      "resolved": "http://registry.npm.taobao.org/http-errors/download/http-errors-1.6.3.tgz",
      "integrity": "sha1-i1VoC7S+KDoLW/TqLjhYC+HZMg0=",
      "requires": {
        "depd": "~1.1.2",
        "inherits": "2.0.3",
        "setprototypeof": "1.1.0",
        "statuses": ">= 1.4.0 < 2"
      }
    },
    "iconv-lite": {
      "version": "0.4.19",
      "resolved": "http://registry.npm.taobao.org/iconv-lite/download/iconv-lite-0.4.19.tgz",
      "integrity": "sha1-90aPYBNfXl2tM5nAqBvpoWA6CCs="
    },
    "inherits": {
      "version": "2.0.3",
      "resolved": "http://registry.npm.taobao.org/inherits/download/inherits-2.0.3.tgz",
      "integrity": "sha1-Yzwsg+PaQqUC9SRmAiSA9CCCYd4="
    },
    "ipaddr.js": {
      "version": "1.8.0",
      "resolved": "http://registry.npm.taobao.org/ipaddr.js/download/ipaddr.js-1.8.0.tgz",
      "integrity": "sha1-6qM9bd16zo9/b+DJygRA5wZzix4="
    },
    "media-typer": {
      "version": "0.3.0",
      "resolved": "http://registry.npm.taobao.org/media-typer/download/media-typer-0.3.0.tgz",
      "integrity": "sha1-hxDXrwqmJvj/+hzgAWhUUmMlV0g="
    },
    "merge-descriptors": {
      "version": "1.0.1",
      "resolved": "http://registry.npm.taobao.org/merge-descriptors/download/merge-descriptors-1.0.1.tgz",
      "integrity": "sha1-sAqqVW3YtEVoFQ7J0blT8/kMu2E="
    },
    "methods": {
      "version": "1.1.2",
      "resolved": "http://registry.npm.taobao.org/methods/download/methods-1.1.2.tgz",
      "integrity": "sha1-VSmk1nZUE07cxSZmVoNbD4Ua/O4="
    },
    "mime": {
      "version": "1.4.1",
      "resolved": "http://registry.npm.taobao.org/mime/download/mime-1.4.1.tgz",
      "integrity": "sha1-Eh+evEnjdm8xGnbh+hyAA8SwOqY="
    },
    "mime-db": {
      "version": "1.36.0",
      "resolved": "http://registry.npm.taobao.org/mime-db/download/mime-db-1.36.0.tgz",
      "integrity": "sha1-UCBHjbPH/pOq17vMTc+GnEM2M5c="
    },
    "mime-types": {
      "version": "2.1.20",
      "resolved": "http://registry.npm.taobao.org/mime-types/download/mime-types-2.1.20.tgz",
      "integrity": "sha1-kwy3GdVx6QNzhSD4RwkRVIyizBk=",
      "requires": {
        "mime-db": "~1.36.0"
      }
    },
    "ms": {
      "version": "2.0.0",
      "resolved": "http://registry.npm.taobao.org/ms/download/ms-2.0.0.tgz",
      "integrity": "sha1-VgiurfwAvmwpAd9fmGF4jeDVl8g="
    },
    "negotiator": {
      "version": "0.6.1",
      "resolved": "http://registry.npm.taobao.org/negotiator/download/negotiator-0.6.1.tgz",
      "integrity": "sha1-KzJxhOiZIQEXeyhWP7XnECrNDKk="
    },
    "on-finished": {
      "version": "2.3.0",
      "resolved": "http://registry.npm.taobao.org/on-finished/download/on-finished-2.3.0.tgz",
      "integrity": "sha1-IPEzZIGwg811M3mSoWlxqi2QaUc=",
      "requires": {
        "ee-first": "1.1.1"
      }
    },
    "parseurl": {
      "version": "1.3.2",
      "resolved": "http://registry.npm.taobao.org/parseurl/download/parseurl-1.3.2.tgz",
      "integrity": "sha1-/CidTtiZMRlGDBViUyYs3I3mW/M="
    },
    "path-to-regexp": {
      "version": "0.1.7",
      "resolved": "http://registry.npm.taobao.org/path-to-regexp/download/path-to-regexp-0.1.7.tgz",
      "integrity": "sha1-32BBeABfUi8V60SQ5yR6G/qmf4w="
    },
    "proxy-addr": {
      "version": "2.0.4",
      "resolved": "http://registry.npm.taobao.org/proxy-addr/download/proxy-addr-2.0.4.tgz",
      "integrity": "sha1-7PxzO/Iv+Mb0B/onUye5q2fki5M=",
      "requires": {
        "forwarded": "~0.1.2",
        "ipaddr.js": "1.8.0"
      }
    },
    "qs": {
      "version": "6.5.1",
      "resolved": "http://registry.npm.taobao.org/qs/download/qs-6.5.1.tgz",
      "integrity": "sha1-NJzfbu+J7EXBLX1es/wMhwNDptg="
    },
    "range-parser": {
      "version": "1.2.0",
      "resolved": "http://registry.npm.taobao.org/range-parser/download/range-parser-1.2.0.tgz",
      "integrity": "sha1-9JvmtIeJTdxA3MlKMi9hEJLgDV4="
    },
    "raw-body": {
      "version": "2.3.2",
      "resolved": "http://registry.npm.taobao.org/raw-body/download/raw-body-2.3.2.tgz",
      "integrity": "sha1-vNYMd9Prk83gBQKVw/N5OJvIj4k=",
      "requires": {
        "bytes": "3.0.0",
        "http-errors": "1.6.2",
        "iconv-lite": "0.4.19",
        "unpipe": "1.0.0"
      },
      "dependencies": {
        "depd": {
          "version": "1.1.1",
          "resolved": "http://registry.npm.taobao.org/depd/download/depd-1.1.1.tgz",
          "integrity": "sha1-V4O04cRZ8G+lyif5kfPQbnoxA1k="
        },
        "http-errors": {
          "version": "1.6.2",
          "resolved": "http://registry.npm.taobao.org/http-errors/download/http-errors-1.6.2.tgz",
          "integrity": "sha1-CgAsyFcHGSp+eUbO7cERVfYOxzY=",
          "requires": {
            "depd": "1.1.1",
            "inherits": "2.0.3",
            "setprototypeof": "1.0.3",
            "statuses": ">= 1.3.1 < 2"
          }
        },
        "setprototypeof": {
          "version": "1.0.3",
          "resolved": "http://registry.npm.taobao.org/setprototypeof/download/setprototypeof-1.0.3.tgz",
          "integrity": "sha1-ZlZ+NwQ+608E2RvWWMDL77VbjgQ="
        }
      }
    },
    "safe-buffer": {
      "version": "5.1.1",
      "resolved": "http://registry.npm.taobao.org/safe-buffer/download/safe-buffer-5.1.1.tgz",
      "integrity": "sha1-iTMSr2myEj3vcfV4iQAWce6yyFM="
    },
    "send": {
      "version": "0.16.2",
      "resolved": "http://registry.npm.taobao.org/send/download/send-0.16.2.tgz",
      "integrity": "sha1-bsyh4PjBVtFBWXVZhI32RzCmu8E=",
      "requires": {
        "debug": "2.6.9",
        "depd": "~1.1.2",
        "destroy": "~1.0.4",
        "encodeurl": "~1.0.2",
        "escape-html": "~1.0.3",
        "etag": "~1.8.1",
        "fresh": "0.5.2",
        "http-errors": "~1.6.2",
        "mime": "1.4.1",
        "ms": "2.0.0",
        "on-finished": "~2.3.0",
        "range-parser": "~1.2.0",
        "statuses": "~1.4.0"
      }
    },
    "serve-static": {
      "version": "1.13.2",
      "resolved": "http://registry.npm.taobao.org/serve-static/download/serve-static-1.13.2.tgz",
      "integrity": "sha1-CV6Ecv1bRiN9tQzkhqQ/S4bGzsE=",
      "requires": {
        "encodeurl": "~1.0.2",
        "escape-html": "~1.0.3",
        "parseurl": "~1.3.2",
        "send": "0.16.2"
      }
    },
    "setprototypeof": {
      "version": "1.1.0",
      "resolved": "http://registry.npm.taobao.org/setprototypeof/download/setprototypeof-1.1.0.tgz",
      "integrity": "sha1-0L2FU2iHtv58DYGMuWLZ2RxU5lY="
    },
    "statuses": {
      "version": "1.4.0",
      "resolved": "http://registry.npm.taobao.org/statuses/download/statuses-1.4.0.tgz",
      "integrity": "sha1-u3PURtonlhBu/MG2AaJT1sRr0Ic="
    },
    "type-is": {
      "version": "1.6.16",
      "resolved": "http://registry.npm.taobao.org/type-is/download/type-is-1.6.16.tgz",
      "integrity": "sha1-+JzjQVQcZysl7nrjxz3uOyvlAZQ=",
      "requires": {
        "media-typer": "0.3.0",
        "mime-types": "~2.1.18"
      }
    },
    "unpipe": {
      "version": "1.0.0",
      "resolved": "http://registry.npm.taobao.org/unpipe/download/unpipe-1.0.0.tgz",
      "integrity": "sha1-sr9O6FFKrmFltIF4KdIbLvSZBOw="
    },
    "utils-merge": {
      "version": "1.0.1",
      "resolved": "http://registry.npm.taobao.org/utils-merge/download/utils-merge-1.0.1.tgz",
      "integrity": "sha1-n5VxD1CiZ5R7LMwSR0HBAoQn5xM="
    },
    "vary": {
      "version": "1.1.2",
      "resolved": "http://registry.npm.taobao.org/vary/download/vary-1.1.2.tgz",
      "integrity": "sha1-IpnwLG3tMNSllhsLn3RSShj2NPw="
    }
  }
}
```
├── .gitlab-ci.yml
├── .gitignore
└── README.md
```yml
# .gitlab-ci.yml
image: node

all_tests:
  script:
   - npm install
   - node index.js

```
```sh
# .gitignore
node_modules/
npm-debug.log*
```
```md
// README.md
test runner
```
3.提交代码，打开工程 CI/CD jobs，会看到构建结果:
![](result.png)

## 结论
至此，简单的 CI 过程搭建完毕，后面就是修改`.gitlab-ci.yml`来实现自己想要的构建结果