#/bin/bash

python3 generateTestSet.py 2009-1-16 2009-2-16 ../Jan1-15/features.db ../Jan1-15/testset.db
python3 generateTestSet.py 2009-2-1 2009-3-1 ../Jan16-31/features.db ../Jan16-31/testset.db
python3 generateTestSet.py 2009-2-16 2009-3-16 ../Feb1-15/features.db ../Feb1-15/testset.db
python3 generateTestSet.py 2009-3-1 2009-4-1 ../Feb16-28/features.db ../Feb16-28/testset.db
python3 generateTestSet.py 2009-3-16 2009-4-16 ../Mar1-15/features.db ../Mar1-15/testset.db
python3 generateTestSet.py 2009-4-1 2009-5-1 ../Mar16-31/features.db ../Mar16-31/testset.db
python3 generateTestSet.py 2009-4-16 2009-5-16 ../Apr1-15/features.db ../Apr1-15/testset.db
python3 generateTestSet.py 2009-2-1 2009-3-1 ../Jan/features.db ../Jan/testset.db
python3 generateTestSet.py 2009-3-1 2009-4-1 ../Feb/features.db ../Feb/testset.db
python3 generateTestSet.py 2009-4-1 2009-5-1 ../Mar/features.db ../Mar/testset.db
python3 generateTestSet.py 2009-4-1 2009-5-1 ../Jan-Mar/features.db ../Jan-Mar/testset.db
python3 generateTestSet.py 2009-5-1 2009-6-1 ../Feb-Apr/features.db ../Feb-Apr/testset.db