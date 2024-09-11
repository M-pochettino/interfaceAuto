class AssertTypeError(Exception):
    """
    自定义异常类：用于处理yaml文件断言模式类型错误的异常。
    """

    def __init__(self, message='不支持该模式断言'):
        """
        初始化异常对象。
        :param message: 异常消息，默认为'不支持该模式断言'
        """
        self.message = message
        super().__init__(self.message)
