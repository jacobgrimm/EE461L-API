import json

from flask import make_response


def sqlToDict(resultproxy):
    d, a = {}, []
    for rowproxy in resultproxy:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)
    return a



class responseFactory :

    @staticmethod
    def NEWpagedRequestRespond(resultproxy, pageNum,formatter, headers,filterType = None):
        a = sqlToDict(resultproxy)
        b = []
        for i in a:
            b.append(formatter(i))
        a = b

        if 'filter' in headers:
           a = filterType(a, headers['filter'])

        info= responseFactory.NEWpageBounds(pageNum,len(a))


        resp = {'response' : 'Success',
        'page_num' : pageNum,
        'results': ''
        }
        if info == None:
            resp['response'] = 'Invalid Page Request'
            resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
        
        bottomIndex, topIndex, resp['pages_total'] = info[0], info[1], info[2]
        final_list = []
        for entry in a[bottomIndex:topIndex]:
            final_list.append((entry))
        resp['results'] = final_list
        resp = make_response(json.dumps(resp, indent=4 ,sort_keys= True))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = 'filter'
        resp.headers['Access-Control-Request-Method'] = 'GET'


        return resp

    @staticmethod
    def NEWindividualRequestRespond(resultproxy, resourceName, formatter):
        resp = {'response' : 'Resource {} Not Found'.format(resourceName),
            'results': 'Please Verify desired resource is present in our database and spelled correctly'}

        a = sqlToDict(resultproxy)
        if a == []:
            resp = make_response(json.dumps(resp, indent=4, sort_keys= True))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
        else:    
            resp['results'] =formatter(a[0])
            resp['response'] = 'Success'
            resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp


    @staticmethod
    def NEWpageBounds(pageNum, numFiles):
        pageNum -= 1
        filesPerPage = 9
        numPages =  int(numFiles / filesPerPage) 
        if (numFiles % filesPerPage) != 0:
            numPages+=1
        if pageNum <0 or pageNum >numPages:
            return None
            
        bottomIndex = pageNum * filesPerPage
        topIndex = (pageNum+1) * filesPerPage
        return(bottomIndex,topIndex,numPages)

    @staticmethod
    def constructIssueFilterResponse(d, headers, pageNum):
        if 'sort' in headers:
            reverse = True
            if headers['sort'] == 'False':
                reverse = False
                d = sorted(d, key=lambda k: k['name'], reverse = reverse)
        else:
                d = sorted(d, key=lambda k: k['name'])
        
        #remove duplicates
        temp = []
        prev = 'TEMP_ISSUE'
        for entry in d:
            if prev != entry['name']:
                temp.append(entry)
            prev = entry['name']
        a = temp


        info= responseFactory.NEWpageBounds(pageNum,len(a))

        resp = {'response' : 'Success',
        'page_num' : pageNum,
        'results': ''
        }
        if info == None:
            resp['response'] = 'Invalid Page Request'
            resp =  make_response(json.dumps(resp, indent=4, sort_keys= True))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
        
        bottomIndex, topIndex, resp['pages_total'] = info[0], info[1], info[2]
        final_list = []
        for entry in a[bottomIndex:topIndex]:
            final_list.append((entry))
        resp['results'] = final_list
        resp = make_response(json.dumps(resp, indent=4 ,sort_keys= True))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = 'filter'
        resp.headers['Access-Control-Request-Method'] = 'GET'
        return resp

