import os
import logging
from ..helpers import run_cmd
from .base import Provider

log = logging.getLogger("__main__")


class RubyGemsProvider(Provider):
    def init_provider(self):
        self.gem_name = self.source_dict["gem_name"]

    def tool_presence_check(self):
        try:
            run_cmd(["which", "rubyporter"])
        except RuntimeError as err:
            log.error("Please, install rubyporter.")
            raise err

    def produce_srpm(self):
        self.tool_presence_check()
        spec = os.path.join(self.resultdir, "rubygem-{0}.spec".format(self.gem_name))

        cmd = ["rubyporter", "-s", self.gem_name, "-o", spec]
        result = run_cmd(cmd)

        if "Empty tag: License" in result.stderr:
            raise RuntimeError("\n".join([
                result.stderr,
                "Not specifying a license means all rights are reserved;"
                "others have no rights to use the code for any purpose.",
                "See http://guides.rubygems.org/specification-reference/#license="]))

        return self.build_srpm_from_spec(spec)
