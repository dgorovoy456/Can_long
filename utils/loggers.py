from allure_commons._allure import StepContext
from loguru import logger


class Logger:
    """
    General Logger class to output debug messages in the specific scope
    """

    def __init__(self,
                 scope_name: str,
                 indentation_level: int = 2,
                 log_level: str = 'debug'
                 ):
        self.scope_name = scope_name
        self.indentation_level = indentation_level
        self.log_level = log_level

        self.indentation = ' ' * 4 * self.indentation_level

    def log(self,
            message: str,
            log_level: str = None
            ) -> None:
        """
        The main method to log messages with specified log level or log level of the
        current Logger object. Messages are formatted in the next way:
            [<scope of the logger>]: <message>

        Possible values of 'log_level' argument are (in order of increasing log severity):
            ['trace', 'debug', 'info', 'success', 'warning', 'error', 'critical']
        """
        if log_level is None:
            log_level = self.log_level
        log_function = getattr(logger, log_level)
        log_message = f"{self.indentation}[{self.scope_name}]: {message}"
        log_function(log_message)


class TestLogger(Logger):
    """
    Logger to output messages in the example_tests and to wrap allure steps for logging
    """

    def __init__(self,
                 scope_name: str,
                 indentation_level: int = 1,
                 log_level: str = 'debug'
                 ):
        super().__init__(scope_name=scope_name,
                         log_level=log_level,
                         indentation_level=indentation_level)

    def step_log(self,
                 step: StepContext,
                 log_level: str = None,
                 ) -> StepContext:
        """
        Used to log allure steps in the test body, common usage is next:

            with step_log(allure.step(title='step title')):
                <step body>
                ...

        Possible values of 'log_level' argument are (in order of increasing log severity):
            ['trace', 'debug', 'info', 'success', 'warning', 'error', 'critical']
        """
        log_message = f"Step - {step.title}"
        self.log(message=log_message,
                 log_level=log_level)
        return step


class FixtureLogger(TestLogger):
    """
    Logger is created to output debug messages in fixtures to track order of
    fixtures execution, designed to call 'log_fixture_started' at the begging of
    target fixture function and 'log_fixture_finished' at the end
    """

    def __init__(self,
                 fixture_name: str,
                 indentation_level: int = 0,
                 log_level: str = 'debug'
                 ):
        super().__init__(scope_name=fixture_name,
                         log_level=log_level,
                         indentation_level=indentation_level)

    def log_fixture_started(self,
                            log_level: str = None
                            ) -> None:
        """
        Should be used at the beginning of the fixture

        Possible values of 'log_level' argument are (in order of increasing log severity):
            ['trace', 'debug', 'info', 'success', 'warning', 'error', 'critical']
        """
        message = f"Started '{self.scope_name}' fixture"
        self.log(message=message,
                 log_level=log_level)

    def log_fixture_finished(self,
                             log_level: str = None
                             ) -> None:
        """
        Should be used at the end of the fixture

        Possible values of 'log_level' argument are (in order of increasing log severity):
            ['trace', 'debug', 'info', 'success', 'warning', 'error', 'critical']
        """
        message = f"Finished '{self.scope_name}' fixture"
        self.log(message=message,
                 log_level=log_level)
