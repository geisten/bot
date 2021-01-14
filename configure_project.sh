PLACEHOLDER_NAME='blueprint'
PROJECT_NAME=$1

echo -e "\nRenaming variables and files...\n"

mv $PLACEHOLDER_NAME $PROJECT_NAME

sed -i s/example/$PROJECT_NAME/g Makefile
sed -i s/$PLACEHOLDER_NAME/$PROJECT_NAME/g Makefile
sed -i s/$PLACEHOLDER_NAME/$PROJECT_NAME/g setup.py

echo -e "\nTesting if everything works...\n"
make test
