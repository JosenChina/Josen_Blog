# _*_ coding: utf-8 _*_
# filename: view.py

from flask import render_template, redirect, flash, url_for, request, current_app
from flask_login import login_required, current_user
from . import _admin
from ._function import clean
from ..models.commentModel import Comment
from ..models.userModel import User
from ..models.sensitiveWordsModel import SensitiveWord
from ..models.commentReportsModel import CommentReport
from webapp.decorators import admin_required
import os
from datetime import datetime

#
# @_admin.route('/comment-enable/<int:bid>/<page>/<int:id>')
# @login_required
# @admin_required
# def comment_enable(bid, page, id):
#     comment = Comment.query.get_or_404(id)
#     comment.disabled = False
#     db.session.add(comment)
#     flash('已启用！')
#     return redirect(url_for('main.look_blog', id=bid, page=page))
#
#
# @_admin.route('/comment-disable/<int:bid>/<page>/<int:id>')
# @login_required
# @admin_required
# def comment_disable(bid, page, id):
#     comment = Comment.query.get_or_404(id)
#     comment.disabled = True
#     db.session.add(comment)
#     flash('已禁用！')
#     return redirect(url_for('main.look_blog', id=bid, page=page))


@_admin.route('/edit-bulletin', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_bulletin():
    with open('%s/bulletin.txt' % os.path.dirname(__file__), 'r') as f:
        bulletin = f.read()
    if request.method == 'POST':
        with open('%s/bulletin.txt' % os.path.dirname(__file__), 'w') as f:
            f.write(clean(request.form['bulletin']))
            # f.write(request.form['bulletin'])
        return redirect(url_for('main.index'))
    return render_template('admin/editBulletin.html', bulletin=bulletin)


@_admin.route('/users-manage', methods=['GET', 'POST'])
@login_required
@admin_required
def users_manage():
    page = request.args.get('page', 1, type=int)
    users = User.query.filter(User.id != current_user.id)
    users_pagination = users.order_by(User.member_since.desc()).paginate(page, current_app.config['FLASKY_USERS_PER_PAGE'], error_out=False)
    un = users.count()
    search_results = None
    sn = 0
    if request.method == 'POST':
        if request.form['submit'] == 'username':
            search_results = User.query.filter(User.username.like('%'+request.form['username']+'%'))\
                .filter(User.id != current_user.id).limit(20)
        elif request.form['submit'] == 'email':
            search_results = User.query.filter(User.email.like('%'+request.form['email']+'%')).\
                filter(User.id != current_user.id).limit(20)
        sn = search_results.count()
    return render_template('admin/usersManage.html', sn=sn, search_results=search_results,
                           users_pagination=users_pagination, un=un)


@_admin.route('/delete-user/<id>')
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    user.delete_user()
    flash('已删除该用户！')
    return redirect(url_for('admin.users_manage'))


@_admin.route('/report-manage')
@login_required
@admin_required
def report_manage():

    return render_template('admin/reportManage.html')


@_admin.route('/add-sensitiveWord', methods=['GET', 'POST'])
@login_required
@admin_required
def add_sensitive_word():
    if request.method == 'POST':
        SW = SensitiveWord.query.filter_by(word=request.form['body']).first() or SensitiveWord(word=request.form['body'])
        SW.ping()
        SW.add_one()
        flash('敏感词已添加！')
        if request.args.get('id', 0, type=int):
            CommentReport.query.get_or_404(request.args.get('id', type=int)).delete_one()
            Comment.query.get_or_404(request.args.get('id', type=int)).disabling()
    return "<script language=javascript>self.location=document.referrer;</script>"


@_admin.route('/delete-report/<int:id>')
@login_required
@admin_required
def delete_report(id):
    CommentReport.query.get_or_404(id).delete_one()
    return redirect(url_for('admin.report_manage'))


@_admin.route('/sensitiveWord-manage')
@login_required
@admin_required
def sensitive_words_manage():
    page = request.args.get('page', 1, type=int)
    SW = SensitiveWord.query
    pagination = SW.order_by(SensitiveWord.timestamp.desc())\
        .paginate(page, current_app.config['FLASKY_SENSITIVEWORD_PER_PAGE'], error_out=False)
    return render_template('admin/sensitiveWordsManage.html', pagination=pagination, SW=SW)


@_admin.route('/delete-sensitiveWord/<int:id>')
@login_required
@admin_required
def delete_sensitive_word(id):
    SensitiveWord.query.get_or_404(id).delete_one()
    return redirect(url_for('admin.sensitive_words_manage'))
