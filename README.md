# DNS Checker (Learning Project)

## Description
This is a simple DNS checker written in Python.

It sends the same DNS query to multiple DNS resolvers stored in a MongoDB database and collects their responses.

This project is built for learning purposes.

---

## Why this project?
DNS results can change depending on:
- Resolver location
- DNS propagation

Using multiple DNS resolvers helps to better understand these differences.


## Technologies Used
- Python 3
- dnspython
- MongoDB
- PyMongo
- ThreadPoolExecutor

