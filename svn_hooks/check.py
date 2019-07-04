# !/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import re
from jira import JIRA


class JiraTool:
    def __init__(self):
        self.server = 'http://mis.rongcard.com/jira'
        self.basic_auth = ('gitlab', '19861029')
        self.timeout = 5
        self.jiraClinet = None

    @property
    def login(self):
        try:
            self.jiraClinet = JIRA(server=self.server, basic_auth=self.basic_auth, timeout=self.timeout)
        except Exception as e:
            return False
        if self.jiraClinet:
            return True
        else:
            return False

    def findIssueById(self, issueId):
        if issueId:
            if self.jiraClinet == None:
                if not self.login:
                    return "JIRA_LOGIN_FAILED"

            try:
                issue = self.jiraClinet.issue(issueId)
            except Exception as e:
                return "ISSUE_NOT_EXIST"

            # issuetype = issue.fields.issuetype.name.encode("utf-8")
            # if issuetype != "需求" :
            #     return "ISSUE_TYPE_ERROR"

            return issue.fields.status.name.encode("utf-8")

        else:
            return 'Please input your issueId'


class Check:
    def __init__(self):
        pass

    # return true or false if this passed string is a valid comment
    def checkIssueKey(self, comment):
        # define regular expression
        p = re.compile('^ISSUE_KEY:\s*([A-Z]+-+[0-9]+)(\s*)(comment_string:+(.*))|^Merge\ branch(.*)')
        matchObj = p.match(comment)
        if matchObj:
            return p.match(comment).group(1)
        else:
            return 0

    def result(self, status, msg=''):
        if status == 1:
            sys.stderr.write(msg.encode("gbk"))
            sys.exit(status)

    def main(self, repos, txn):
        log_file = '%s\\log_msg_%s.txt' % (repos, txn)
        log_msg = ''
        with open(log_file, 'r') as f:
            for line in f.readlines():
                log_msg = log_msg + line
        os.remove(log_file)

        issueKey = self.checkIssueKey(log_msg)
        if not issueKey:
            err_msg ='''
#####################################
##Commit message style check failed.                          ##
##Example:                                                              ##
##    ISSUE_KEY:JIRA-111 需求ID                               ##
##    comment_string:注释信息                                   ##
#####################################
'''
            self.result(1, err_msg)

        jiraTool = JiraTool()
        issue = jiraTool.findIssueById(issueKey)
        if issue == "JIRA_LOGIN_FAILED":
            self.result(1, "Jira登录失败，请联系管理员！！！\n")
        elif issue == "ISSUE_NOT_EXIST":
            self.result(1, "未找到需求ID，请先创建需求！！！\n")
        elif issue == "测试通过" or issue == "申请通过":
            self.result(0)
        else:
            self.result(1, "需求状态为" + issue + "，请先修改状态！！！\n")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: %s REPOS TXN\n" % (sys.argv[0]))
    else:
        check = Check()
        check.main(sys.argv[1], sys.argv[2])
