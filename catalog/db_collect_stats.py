#!/usr/bin/env python

import os
import sys
import argparse
# import robot

# Determine BigRobot path(s) based on this executable (which resides in
# the bin/ directory.
bigrobot_path = os.path.dirname(__file__) + '/..'
exscript_path = bigrobot_path + '/vendors/exscript/src'

sys.path.insert(0, bigrobot_path)
sys.path.insert(1, exscript_path)

import autobot.helpers as helpers
from catalog_modules.test_catalog import TestCatalog
from catalog_modules.build_stats import BuildStats

helpers.set_env('IS_GOBOT', 'False')
helpers.set_env('AUTOBOT_LOG', './myrobot.log')


def print_stat3(descr, val, pct=None):
    if pct != None:
        print("%-74s %22s  %.1f%%" %
              (descr, val, pct))
    else:
        print("%-74s %22s" % (descr, val))


def print_stat2(descr, val, untested=None, manual=None, test_pct=None,
                pass_pct=None, automation_pct=None):
    if automation_pct != None:
        print("%-74s %22s  %-22s %-12s %8.1f%% %5.1f%% %5.1f%%" %
              (descr,
               val,
               "manual-untested(%s)" % untested,
               "manual(%s)" % manual,
               test_pct,
               pass_pct,
               automation_pct))
    elif pass_pct != None:
        print("%-74s %22s  %-22s %-12s %8.1f%% %5.1f%%" %
              (descr,
               val,
               "manual-untested(%s)" % untested,
               "manual(%s)" % manual,
               test_pct,
               pass_pct))
    elif test_pct != None:
        print("%-74s %22s  %-22s %-12s %8.1f%%" %
              (descr,
               val,
               "manual-untested(%s)" % untested,
               "manual(%s)" % manual,
               test_pct))
    elif manual != None:
        print("%-74s %22s  %-22s %-12s" %
              (descr,
               val,
               "manual-untested(%s)" % untested,
               "manual(%s)" % manual))
    elif untested != None:
        print("%-74s %22s  %-22s" %
              (descr, val, "manual-untested(%s)" % untested))
    else:
        print("%-74s %22s" % (descr, val))


def print_stat(descr, val, untested=None, test_pct=None, manual=None):
    if manual != None:
        print("%-74s %22s  %-22s %8.1f%%  %s" %
              (descr,
               val,
               "manual-untested(%s)" % untested,
               test_pct,
               "manual(%s)" % manual))
    elif test_pct != None:
        print("%-74s %22s  %-22s %8.1f%%" %
              (descr, val, "manual-untested(%s)" % untested, test_pct))
    elif untested != None:
        print("%-74s %22s  %-22s" %
              (descr, val, "manual-untested(%s)" % untested))
    else:
        print("%-74s %22s" % (descr, val))


def print_testcases(testcases):
    i = 0
    for tc in sorted(testcases):
        i += 1
        print("\t%03d. %s" % (i, helpers.utf8(tc)))
    if i > 0:
        print("")


def print_suites(suites):
    i = 0
    total_tests = 0
    for n in suites:
        i += 1
        print("\t%3d. %-15s (%3s test cases) %s" %
              (i, n['author'], n['total_tests'], n['product_suite']))
        total_tests += n['total_tests']
    print_stat("Total test cases executed:", total_tests)


def print_suites_not_executed(suites, suites_executed):
    suite_executed_lookup = {}
    for n in suites_executed:
        name = n['product_suite']
        suite_executed_lookup[name] = True
    i = 0
    total_tests = 0
    for n in suites:
        name = n['product_suite']
        if name not in suite_executed_lookup:
            i += 1
            print("\t%3d. %-15s (%3s test cases) %s" %
                  (i, n['author'], n['total_tests'], name))
            total_tests += n['total_tests']
    print_stat("Total test cases not executed:", total_tests)


def percentage(a, total):
    if float(total) == 0.0:
        return 0.0  # avoid divide by zero
    else:
        return float(a) / float(total) * 100.0


def prog_args():
    descr = """\
Display test execution stats collected for a specific build.
"""
    parser = argparse.ArgumentParser(prog='db_collect_stats',
                                     description=descr)
    parser.add_argument('--release', required=True,
                        help=("Product release, e.g., 'IronHorse'"))
    parser.add_argument('--build',
                        help=("Jenkins build string,"
                              " e.g., 'bvs master #2007'"))
    parser.add_argument('--show-untested', action='store_true', default=False,
                        help=("Show the manual-untested test cases"))
    parser.add_argument('--show-suites', action='store_true', default=False,
                        help=("Show the test suites"))
    parser.add_argument('--show-all', action='store_true', default=False,
                        help=("Show all stats"))
    parser.add_argument('--no-show-functional-areas', action='store_true',
                        default=False,
                        help=("Don't show test details for functional areas"))
    _args = parser.parse_args()

    # _args.build <=> env BUILD_NAME
    if not _args.build and 'BUILD_NAME' in os.environ:
        _args.build = os.environ['BUILD_NAME']
    elif not _args.build:
        helpers.error_exit("Must specify --build option or set environment"
                           " variable BUILD_NAME")
    else:
        os.environ['BUILD_NAME'] = _args.build

    return _args


def display_stats(args):
    build = args.build
    ih = BuildStats(args.release, build)
    total = {}
    cat = TestCatalog()

    if args.show_all:
        print_stat("Total of all test suites:", ih.total_testsuites())
        print_stat("Total of all test cases:", ih.total_testcases())

    suites_in_release = ih.testsuites(release=ih.release_lowercase())
    product_suites = {}
    for _suites in suites_in_release:
        product_suites[_suites['product_suite']] = _suites


    print ""
    print "%s Release Metrics" % (ih.release())
    print "==================================================================="
    total_testsuites_in_release = ih.total_testsuites(
               release=ih.release_lowercase())
    print_stat("Total test suites:", total_testsuites_in_release)

    total_tc = ih.total_testcases(release=ih.release_lowercase())
    total_tc_untested = ih.total_testcases_by_tag(["manual-untested"])[0]
    total_tc_manual = ih.total_testcases_by_tag(["manual"])[0]
    total_tc_pct = percentage(total_tc - total_tc_untested, total_tc)
    print_stat2("Total test cases:", total_tc)
    total['tests'] = total_tc


    for functionality in cat.test_types() + ["manual", "manual-untested"]:
        total_tc_func = ih.total_testcases_by_tag(functionality)[0]
        total_tc_func_untested = ih.total_testcases_by_tag(
                                    [functionality, "manual-untested"])[0]
        total_tc_func_manual = ih.total_testcases_by_tag(
                                    [functionality, "manual"])[0]
        test_pct = percentage(total_tc_func - total_tc_func_untested,
                              total_tc_func)
        total[functionality] = total_tc_func


    total_manual = ih.total_testcases_by_tag('manual')[0]
    print_stat3("Total manual test cases:",
                total_manual,
                percentage(total_manual, total_tc))
    total_untested = ih.total_testcases_by_tag('manual-untested')[0]
    print_stat3("Total manual-untested test cases:",
                total_untested,
                percentage(total_untested, total_tc))


    total_tc_executable = ih.total_executable_testcases()
    print_stat3("Total test cases executable:",
               total_tc_executable,
               percentage(total_tc_executable, total_tc))


    total_tc_automated = total_tc - total_tc_manual - total_tc_untested


    # total_tc_automated_executable = total_tc_executable - total_tc_manual
    print_stat3("Total test cases automated:",
               total_tc_automated,
               percentage(total_tc_automated, total_tc))


    print ""
    print "Regression Run Results (Build: %s)" % (build)
    i = 0
    for a_build in cat.aggregated_build(build):
        i += 1
        print "\tBuild %02d: %s" % (i, a_build)
    print "==================================================================="


    total_testsuites_in_release_executed = ih.total_testsuites_executed(
               build_name=build)[0]
    print_stat("Total test suites executed:",
               total_testsuites_in_release_executed)
    if args.show_suites:
        suites_executed = ih.testsuites(
                               release=ih.release_lowercase(),
                               build=build,
                               collection_testcases="test_cases_archive")
        print_suites(suites_executed)
        print ""

    print_stat("Total test suites not executed:",
               total_testsuites_in_release - total_testsuites_in_release_executed)

    if args.show_suites:
        print_suites_not_executed(suites_in_release, suites_executed)


    print ""
    print "Test Summary                                                                                                                               exec%  pass%  auto%"
    print "--------------------------------------------------------------------------  ---------------------  --------------------   --------------   -----  -----  -----"
    total_executed = ih.total_testcases_executed(build_name=build)
    total_untested = ih.total_testcases_by_tag(
                                    ["manual-untested"])[0]
    total_manual = ih.total_testcases_by_tag(
                                    ["manual"])[0]
    test_pct = percentage(total_executed[0], total['tests'])
    pass_pct = percentage(total_executed[1], total_executed[0])

    total_tc_automated = total['tests'] - total_untested - total_manual
    automation_pct = percentage(total_tc_automated, total['tests'])

    print_stat2("Total test cases (total, executed, passed, failed):",
               (total['tests'],) + total_executed,
               total_untested,
               total_manual,
               test_pct,
               pass_pct,
               automation_pct,
               )
    if args.show_untested:
        print_testcases(ih.manual_untested_by_tag())

    for functionality in cat.test_types() + ["manual", "manual-untested"]:
        total_executed = ih.total_testcases_by_tag_executed(functionality)
        total_untested = ih.total_testcases_by_tag([functionality,
                                                    "manual-untested"])[0]
        total_manual = ih.total_testcases_by_tag([functionality,
                                                    "manual"])[0]
        test_pct = percentage(total_executed[0], total[functionality])
        pass_pct = percentage(total_executed[1], total_executed[0])

        if functionality in ['manual', 'manual-untested']:
            automation_pct = 0.0
        else:
            total_tc_automated = total[functionality] - total_untested - total_manual
            automation_pct = percentage(total_tc_automated, total[functionality])
        print_stat2("Total %s tests (total, executed, passed, failed):"
                   % functionality,
                   (total[functionality],) + total_executed,
                   total_untested,
                   total_manual,
                   test_pct,
                   pass_pct,
                   automation_pct,
                   )
        if args.show_untested:
            print_testcases(ih.manual_untested_by_tag(functionality))

    if not args.no_show_functional_areas:
        print ""
        print "Functional Areas                                                                                                                           exec%  pass%  auto%"
        print "--------------------------------------------------------------------------  ---------------------  --------------------   --------------   -----  -----  -----"
        functionality = "feature"
        for feature in cat.features(release=ih.release_lowercase()):
            total_tc = ih.total_testcases_by_tag([functionality, feature])[0]
            total_executed = ih.total_testcases_by_tag_executed([functionality,
                                                                 feature])
            total_untested = ih.total_testcases_by_tag([functionality, feature,
                                                  "manual-untested"])[0]
            total_manual = ih.total_testcases_by_tag([functionality, feature,
                                                  "manual"])[0]
            test_pct = percentage(total_executed[0], total_tc)
            pass_pct = percentage(total_executed[1], total_executed[0])
            total_tc_automated = total_tc - total_untested - total_manual
            automation_pct = percentage(total_tc_automated, total_tc)
            print_stat2("Total %s+%s tests (total, executed, passed, failed):"
                       % (functionality, feature),
                       (total_tc,) + total_executed,
                       total_untested,
                       total_manual,
                       test_pct,
                       pass_pct,
                       automation_pct,
                       )
            if args.show_untested:
                print_testcases(ih.manual_untested_by_tag([functionality,
                                                           feature]))

    print ""
    print "Manual Verification Details"
    print "==================================================================="
    test_case_cursor = cat.find_test_cases_archive_matching_build(build_name=build)
    # print "Total test cases for build '%s': %s" % (build, test_case_cursor.count())
    i = 0
    for test_case in test_case_cursor:
        if (('jira' in test_case and test_case['jira']) or
            ('notes' in test_case and test_case['notes'])):
            i += 1
            author = product_suites[test_case['product_suite']]['author']
            jira = test_case['jira']
            if test_case['jira']:
                jira += " - https://bigswitch.atlassian.net/browse/%s" % test_case['jira']

            print "%03d. %s  %s  %s" % (i, author, test_case['product_suite'], test_case['name'])
            print "\tverified in : %s" % test_case['build_name_verified']
            print "\tjira        : %s" % jira
            print "\tstatus      : %s" % test_case['status']
            print "\tnotes       : %s" % test_case['notes']
            print ""
    if i == 0:
        print "None"


if __name__ == '__main__':
    display_stats(prog_args())
