# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime
import pytz
import logging

_logger = logging.getLogger(__name__)


class StockEntrust(osv.osv):
    """
    委托单
    """

    _name = "stock.entrust"
    _order = "report_time desc"

    _columns = {
        'business_amount': fields.integer(u"成交数量", size=32, required=True),
        'business_price': fields.float(u"成交价格", size=32, required=True),
        'entrust_amount': fields.integer(u"委托数量", size=32, required=True),
        'entrust_bs': fields.selection((('buy', u'买入'), ('sale', u'卖出')), u'买卖方向'),
        'entrust_no': fields.integer(u"委托编号", required=True),
        'entrust_price': fields.char(u"委托价格", required=True),
        'state': fields.selection((('cancel', u'废单'), ('report', u'已报')), u'委托状态'),
        'report_time': fields.datetime(u"申报时间", required=True),
        'stock_code': fields.char(u"证券代码"),
        'stock_name': fields.char(u"证券名称"),
        'stock_id': fields.many2one('stock.basics', u'股票', required=True),
    }

    def get_now_time(self, cr, uid, ids, context=None):
        """获取当前时间"""
        tz = pytz.timezone('UTC')
        return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

    _defaults = {
        'entrust_no': '000000',
        'entrust_bs': 'buy',
        'state': 'report',
        'business_price': 0.00,
        'business_amount': 0,
        'report_time': get_now_time,
    }

    def button_cancel(self, cr, uid, ids, context=None):
        '''
         取消状态.
        '''
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def create(self, cr, uid, vals, context=None):

        """重写创建方法
        """
        _logger.debug(u"run 委托单 -> create!")

        # 首先要区分是买入还是卖出
        if vals['entrust_bs'] == 'buy':
            # 买入

            # todo 可能要检查是否是买入时间

            # 检查是否足够的资金操作
            CNY_balance = self.pool.get("stock.balance").get_CNY_balance(cr, uid, context)

            if CNY_balance is None:
                raise osv.except_osv(u"错误", u"没有可用的人民币资产")
            # _logger.debug(u"--->可用资金:" + str(CNY_balance.enable_balance))

            # 如果可用资金不足以买入股票
            handle_balance = vals['entrust_amount'] * vals['entrust_price']
            if CNY_balance.enable_balance < handle_balance:
                raise osv.except_osv(u"错误", u"可用资金不足,无法买入")

            # todo 没有问题的话, 调用买入股票接口(还需要处理返回的委托单号)
            self.buy_stock(cr, uid, context)
        else:
            # todo 卖出
            pass

        basics_obj = self.pool.get('stock.basics')
        stock_obj = basics_obj.read(cr, uid, vals['stock_id'], ['name', 'code', 'id'], context)
        vals['stock_name'] = stock_obj['name']
        vals['stock_code'] = stock_obj['code']

        # todo 更新资金

        return super(StockEntrust, self).create(cr, uid, vals, context)

    def buy_stock(self, cr, uid, context=None):
        """
        创建真实买入委托单
        :param cr:
        :param uid:
        :param context:
        :return:
        """
        # todo 待实现
        pass

    def sell_stock(self, cr, uid, context=None):
        """
        创建真实卖出委托单
        :param cr:
        :param uid:
        :param context:
        :return:
        """
        # todo 待实现
        pass

    def onchange_stock(self, cr, uid, ids, stock_id, context=None):
        values = {'value': {}}
        stock = self.pool.get('stock.basics').browse(cr, uid, stock_id, context=context)
        values['value']['entrust_price'] = stock.current_price
        return values













