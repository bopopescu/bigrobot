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
        print("%-74s %24s  %.1f%%" %
              (descr, val, pct))
    else:
        print("%-74s %24s" % (descr, val))


def print_stat2(descr, val, untested=None, manual=None, test_pct=None,
                pass_pct=None, automation_pct=None):
    if automation_pct != None:
        print("%-74s %24s  %-22s %-12s %8.1f%% %5.1f%% %5.1f%%" %
              (descr,
               val,
               "manual-untested(%s)" % untested,
               "manual(%s)" % manual,
               test_pct,
               pass_pct,
               automation_pct))
    elif pass_pct != None:
        print("%-74s %24s  %-22s %-12s %8.1f%% %5.1f%%" %
              (descr,
               val,
               "manual-untested(%s)" % untested,
               "manual(%s)" % manual,
               test_pct,
               pass_pct))
    elif test_pct != None:
        print("%-74s %24s  %-22s %-12s %8.1f%%" %
              (descr,
               val,
               "manual-untested(%s)" % untested,
               "manual(%s)" % manual,
               test_pct))
    elif manual != None:
        print("%-74s %24s  %-22s %-12s" %
              (descr,
               val,
               "manual-untested(%s)" % untested,
               "manual(%s)" % manual))
    elif untested != None:
        print("%-74s %24s  %-22s" %
              (descr, val, "manual-untested(%s)" % untested))
    else:
        print("%-74s %24s" % (descr, val))


def print_stat(descr, val, untested=None, test_pct=None, manual=None):
    if manual != None:
        print("%-74s %24s  %-22s %8.1f%%  %s" %
              (descr,
               val,
               "manual-untested(%s)" % untested,
               test_pct,
               "manual(%s)" % manual))
    elif test_pct != None:
        print("%-74s %24s  %-22s %8.1f%%" %
              (descr, val, "manual-untested(%s)" % untested, test_pct))
    elif untested != None:
        print("%-74s %24s  %-22s" %
              (descr, val, "manual-untested(%s)" % untested))
    else:
        print("%-74s %24s" % (descr, val))


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
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=descr)
    parser.add_argument('--release',
                        help=("Product release, e.g., 'ironhorse', 'ironhorse-plus', 'jackfrost', etc."))
    parser.add_argument('--build',
                        help=("Jenkins build string,"
                              " e.g., 'bvs main #2007'"))
    parser.add_argument('--show-untested', action='store_true', default=False,
                        help=("Show the manual-untested test cases"))
    parser.add_argument('--show-manual', action='store_true', default=False,
                        help=("Show the manual test cases"))
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

    # _args.release <=> env RELEASE_NAME
    if not _args.release and 'RELEASE_NAME' in os.environ:
        _args.release = os.environ['RELEASE_NAME']
    elif not _args.release:
        helpers.error_exit("Must specify --release option or set environment"
                           " variable RELEASE_NAME")
    else:
        os.environ['RELEASE_NAME'] = _args.release
    _args.release = _args.release.lower()

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
    # total_tc_pct = percentage(total_tc - total_tc_untested, total_tc)
    print_stat2("Total test cases:", total_tc)
    total['tests'] = total_tc


    # !!! FIXME: unspecified-topology will need to be removed.
    for functionality in cat.test_types() + ["virtual",
                                             "physical",
                                             "unspecified-topology",
                                             "generic-topology",
                                             "missing-topology",
                                             "manual",
                                             "manual-untested"]:
        total_tc_func = ih.total_testcases_by_tag(functionality)[0]
        # total_tc_func_untested = ih.total_testcases_by_tag(
        #                            [functionality, "manual-untested"])[0]
        # total_tc_func_manual = ih.total_testcases_by_tag(
        #                            [functionality, "manual"])[0]
        # test_pct = percentage(total_tc_func - total_tc_func_untested,
        #                      total_tc_func)
        total[functionality] = total_tc_func


    total_virtual = ih.total_testcases_by_tag('virtual')[0]
    print_stat3("Total virtual test cases:",
                total_virtual,
                percentage(total_virtual, total_tc))
    total_physical = ih.total_testcases_by_tag('physical')[0]
    print_stat3("Total physical test cases:",
                total_physical,
                percentage(total_physical, total_tc))
    total_unspecified_topology = ih.total_testcases_by_tag('unspecified-topology')[0]
    print_stat3("Total unspecified-topology test cases:",
                total_unspecified_topology,
                percentage(total_unspecified_topology, total_tc))
    total_generic_topology = ih.total_testcases_by_tag('generic-topology')[0]
    print_stat3("Total generic-topology test cases:",
                total_generic_topology,
                percentage(total_generic_topology, total_tc))
    total_missing_topology = ih.total_testcases_by_tag('missing-topology')[0]
    print_stat3("Total missing-topology test cases:",
                total_missing_topology,
                percentage(total_missing_topology, total_tc))
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
    print "Test Summary                                                                                                                                 exec%  pass%  auto%"
    print "--------------------------------------------------------------------------  -----------------------  --------------------   --------------   -----  -----  -----"
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
    if args.show_untested and total_untested != 0:
        print "\t----- manual-untested(%d)" % total_untested
        print_testcases(ih.manual_untested_by_tag())
    if args.show_manual and total_manual != 0:
        print "\t----- manual(%d)" % total_manual
        print_testcases(ih.manual_by_tag())

    for functionality in cat.test_types() + ['virtual',
                                             'physical',
                                             'unspecified-topology',
                                             'generic-topology',
                                             'missing-topology',
                                             "manual",
                                             "manual-untested"]:
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
        if args.show_untested and total_untested != 0:
            print "\t----- manual-untested(%d)" % total_untested
            print_testcases(ih.manual_untested_by_tag(functionality))
        if args.show_manual and total_manual != 0:
            print "\t----- manual(%d)" % total_manual
            print_testcases(ih.manual_by_tag(functionality))

    if not args.no_show_functional_areas:
        print ""
        print "Functional Areas                                                                                                                             exec%  pass%  auto%"
        print "--------------------------------------------------------------------------  -----------------------  --------------------   --------------   -----  -----  -----"
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
            if args.show_untested and total_untested != 0:
                print "\t----- manual-untested(%d)" % total_untested
                print_testcases(ih.manual_untested_by_tag([functionality,
                                                           feature]))
            if args.show_manual and total_manual != 0:
                print "\t----- manual(%d)" % total_manual
                print_testcases(ih.manual_by_tag([functionality, feature]))

    print ""
    print "Manual Verification Details"
    print "==================================================================="
    # test_case_cursor = cat.find_test_cases_archive_matching_build(build_name=build)
    test_case_cursor = ih.testcases_archive(release=ih.release_lowercase(), build=build)
    # print "Total test cases for build '%s': %s" % (build, test_case_cursor.count())
    i = 0
    pass_rate = {}
    details_str = ""

    # print "XXXX release: %s, build: %s, tc total: %s" % (ih.release_lowercase(),
    #                                                build,
    #                                                test_case_cursor.count())
    for test_case in test_case_cursor:
        # if (('jira' in test_case and test_case['jira']) or
        #    ('notes' in test_case and test_case['notes'])):

        if 'build_name_verified' in test_case:
            i += 1

            if test_case['product_suite'] in product_suites:
                author = helpers.utf8(product_suites[test_case['product_suite']]['author'])
            else:
                author = 'unknown'

            if author in pass_rate:
                pass_rate[author][test_case['status']] += 1
            else:
                pass_rate[author] = { 'PASS':0, 'FAIL':0 }
                pass_rate[author][test_case['status']] += 1

            if 'build_name_verified' in test_case and test_case['build_name_verified']:
                build_name_verified = test_case['build_name_verified']
            else:
                build_name_verified = None

            if 'jira' in test_case and test_case['jira']:
                jira = test_case['jira']
            else:
                jira = None

            if 'notes' in test_case and test_case['notes']:
                notes = test_case['notes']
            else:
                notes = None

            if jira:
                jira += " - https://bigswitch.atlassian.net/browse/%s" % jira

            details_str += "%03d. %s  %s  %s\n" % (i, author, test_case['product_suite'], test_case['name'])
            details_str += "\tverified in : %s\n" % build_name_verified
            details_str += "\tstatus      : %s\n" % test_case['status']
            details_str += "\tjira        : %s\n" % jira
            details_str += "\tnotes       : %s\n" % notes
            details_str += ""

    if i == 0:
        print "None"
    else:
        total_passes = total_fails = 0
        for author, status in pass_rate.items():
            print "Author: %14s  Passes: %3d  Fails: %3d  Total: %3d" % (author, status['PASS'], status['FAIL'], status['PASS'] + status['FAIL'])
            total_passes += status['PASS']
            total_fails += status['FAIL']
        print "        %14s  Passes: %3d  Fails: %3d  Total: %3d" % ('Combined', total_passes, total_fails, total_passes + total_fails)
        print ""
        print details_str


if __name__ == '__main__':
    display_stats(prog_args())
