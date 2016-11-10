import os
import yaml


def loadSchema(schemaFile):
    try:
        # Check api operation schema file exists
        if not os.path.isfile(schemaFile):
            return (False,
                    "Error: Schema file '" + schemaFile + "' does not exists.")

        # load api operation schema file and return
        try:
            code = open(schemaFile)
        except IOError as exc:
            return (False,
                    "Error loading schema file '" + schemaFile + "': " + exc)

        # Parse schema file
        try:
            config = yaml.load(code)
        except yaml.YAMLError as exc:
            error_pos = ""
            if hasattr(exc, 'problem_mark'):
                error_pos = " at position: (%s:%s)" % (
                    exc.problem_mark.line + 1,
                    exc.problem_mark.column + 1)
            msg = "Error loading schema file '" + schemaFile + "'" + error_pos \
                + ": content format error: Failed to parse yaml format"
            return False, msg

    except Exception as e:
        return (False, "Error loading api operation schema file '%s': %s" % (
            schemaFile, str(e)))

    return (True, config)
