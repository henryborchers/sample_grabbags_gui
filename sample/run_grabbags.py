import os
from grabbags.grabbags import validate_bag, LOGGER, clean_bag, make_bag, _
import bagit
from argparse import Namespace

def run(directories):
    successes = []
    failures = []
    args = Namespace()
    args.processes = 1
    args.fast = False
    args.checksums = True
    args.no_system_files = False
    args.bag_info = {}
    args.clean = False
    args.validate = False
    for bag_parent in directories:
        for bag_dir in filter(lambda i: i.is_dir(), os.scandir(bag_parent)):
            if args.validate:
                action = 'validated'
                try:
                    validate_bag(bag_dir, args)
                    successes.append(bag_dir.path)
                except bagit.BagError as e:
                    LOGGER.error(
                        _("%(bag)s is invalid: %(error)s"),
                        {"bag": bag_dir.path, "error": e}
                    )
                    failures.append(bag_dir.path)
            elif args.clean:
                action = 'cleaned'
                try:
                    clean_bag(bag_dir)
                    successes.append(bag_dir.path)
                except bagit.BagError as e:
                    LOGGER.error(
                        _("%(bag)s cannot be cleaned: %(error)s"),
                        {"bag": bag_dir.path, "error": e}
                    )
                    failures.append(bag_dir.path)
            else:
                action = 'created'
                try:
                    make_bag(bag_dir, args)
                    successes.append(bag_dir.path)
                except bagit.BagError as e:
                    LOGGER.error(
                        _("%(bag)s could not be bagged: %(error)s"),
                        {"bag": bag_dir.path, "error": e}
                    )
                    failures.append(bag_dir.path)

    LOGGER.warning(
        _("%(count)s bags %(action)s successfully"),
        {"count": len(successes), "action": action}
    )
    LOGGER.warning(
        _("%(count)s bags not %(action)s"),
        {"count": len(failures), "action": action}
    )
    if failures:
        LOGGER.warning(
            _("Failed for the following folders: %s"),
            ", ".join(failures)
        )
