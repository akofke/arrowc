#!/usr/bin/env python
import betterast
from arrowc.arrowlang_types import Type



class Node(betterast.Node):
    def __init__(self, node_type, node_data=None, arrowtype=None):
        """
        :type node_type: basestring
        :type node_data: basestring
        :type arrowtype: Type

        :param node_type:
        :param node_data:
        :param arrowtype:
        :return:
        """
        super(Node, self).__init__("{}{}{}".format(
            node_type,
            ",{}".format(node_data) if node_data else "",
            ":{!s}".format(arrowtype) if arrowtype else ""
        ))
        self.node_type = node_type
        self.node_data = node_data
        self.arrowtype = arrowtype









def main():
    ast = Node("blah").addkid(Node("blah2", "x", Type("unit")))
    print ast

if __name__ == '__main__':
    main()