#!/bin/sh
# A few tests with valid and invalid build strings.


echo ""
echo "Below examples are expected to pass"
echo "----"

# BigTap
./build_name_gen.py --testbed common --version-str "Big Tap Controller 4.1.1  (2014.11.13.1922-b.bsc.corsair-4.1.1beta"
./build_name_gen.py --testbed Dell   --version-str "Big Tap Controller 4.0.0  (2014.11.13.1922-b.bsc.corsair-4.1.1beta"
./build_name_gen.py --testbed Accton --version-str "Big Tap Controller 4.0.1  (2014.11.13.1922-b.bsc.corsair-4.1.1beta"
./build_name_gen.py --testbed Quanta --version-str "Big Tap Controller 4.0.2  (2014.11.13.1922-b.bsc.corsair-4.1.1beta"
./build_name_gen.py --testbed Common --version-str "Big Tap Controller 4.1.0  (2014.11.13.1922-b.bsc.corsair-4.1.1beta"
./build_name_gen.py --testbed Common --version-str "Big Tap Controller 4.5.0  (2014.11.13.1922-b.bsc.corsair-4.1.1beta"

# BCF
./build_name_gen.py --testbed 10G     --version-str "Big Cloud Fabric Appliance 3.0.0-main01-SNAPSHOT (bcf_main #4201)"
./build_name_gen.py --testbed virtual --version-str "Big Cloud Fabric Appliance 2.0.0-main01-SNAPSHOT (ihplus_bcf #515)"
./build_name_gen.py --testbed common  --version-str "Big Cloud Fabric Appliance 2.5.0-main01-SNAPSHOT (ihplus_bcf #515)" --additional-version-descr "Testing"



echo ""
echo "Below examples are expected to fail"
echo "----"

# BigTap
./build_name_gen.py --testbed Common --version-str "Big Tape Controller 4.1.2  (2014.11.13.1922-b.bsc.corsair-4.1.1beta"
./build_name_gen.py --testbed Common --version-str "Big Tap Controller 4.1.2  (2014.11.13.1922-b.bsc.corsair-4.1.1beta"
./build_name_gen.py --testbed Common --version-str "Big Tap Controller 4.5.1  (2014.11.13.1922-b.bsc.corsair-4.1.1beta"
./build_name_gen.py --testbed Dell --version-str "Big Tap Controller 5.0.1  (2014.11.13.1922-b.bsc.corsair-4.1.1beta"

# BCF
./build_name_gen.py --testbed virtual --version-str "Big Cloud Fabric Appliance 2.0.0-main01-SNAPSHOT (ihwill_bcf #515)"
