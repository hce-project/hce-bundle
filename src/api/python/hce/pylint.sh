#!/bin/bash

echo "" > $0.log
#pylint --ignore=url_normalize.py --rcfile=./pylintrc --msg-template="{msg_id}:{line:3d},{column:2d}:{msg}" app/*.py >> $0.log
#pylint --rcfile=./pylintrc --msg-template="{msg_id}:{line:3d},{column:2d}:{msg}" dc/*.py >> $0.log
#pylint --rcfile=./pylintrc --msg-template="{msg_id}:{line:3d},{column:2d}:{msg}" dc_crawler/CrawlerTask.py >> $0.log
#pylint --rcfile=./pylintrc --msg-template="{msg_id}:{line:3d},{column:2d}:{msg}" dc_db/*.py >> $0.log
pylint --ignore="alchemyapi.py,alchemy_extractor.py" --rcfile=./pylintrc --msg-template="{msg_id}:{line:3d},{column:2d}:{msg}" dc_processor/*.py >> $0.log
#pylint --rcfile=./pylintrc --msg-template="{msg_id}:{line:3d},{column:2d}:{msg}" dcc/*.py >> $0.log
#pylint --rcfile=./pylintrc --msg-template="{msg_id}:{line:3d},{column:2d}:{msg}" drce/*.py >> $0.log
#pylint --rcfile=./pylintrc --msg-template="{msg_id}:{line:3d},{column:2d}:{msg}" dtm/*.py >> $0.log
#pylint --rcfile=./pylintrc --msg-template="{msg_id}:{line:3d},{column:2d}:{msg}" dtma/*.py >> $0.log
#pylint --rcfile=./pylintrc --msg-template="{msg_id}:{line:3d},{column:2d}:{msg}" dtmc/*.py >> $0.log
#pylint --rcfile=./pylintrc --msg-template="{msg_id}:{line:3d},{column:2d}:{msg}" transport/*.py >> $0.log
