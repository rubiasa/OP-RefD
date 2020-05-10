# -*- coding: utf-8 -*-
"""

@author: rubiaalmeida

# Rubia Almeida 2019-04-13
# Modified:  2019-04-13

"""

from SPARQLWrapper import SPARQLWrapper, JSON, URLENCODED, POSTDIRECTLY
from SPARQLWrapper.Wrapper import QueryResult
#, jsonlayer
try:
    import configparser
except:
    from six.moves import configparser
import math
import json
import spacy
from retry import retry
from sematch.semantic.similarity import EntitySimilarity
import requests
import numpy as np
import csv
import pandas
import ast
from datetime import datetime
from time import sleep
#nlp = spacy.load('en')
#nlp = spacy.load('en_core_web_lg')


class SemRefDRubia:


    #Funcion Indicador
    fun_indi = "PREFIX :     <http://dbpedia.org/resource/> \
                 PREFIX dbo:     <http://dbpedia.org/ontology/> \
                 PREFIX dbp:     <http://dbpedia.org/property/> \
                 SELECT DISTINCT ?s1 FROM <http://dbpedia.org> WHERE  { \
                 ?s1 ?p1 %s  . \
                 FILTER(?p1 NOT IN (dbo:wikiPageDisambiguates, dbp:wikiPageUsesTemplate, dbo:wikiPageRedirects)) \
                 FILTER(STRSTARTS(STR(?s1), 'http://dbpedia.org/resource/')) \
                 }";

    #Funcion Indicador Count
    fun_indi_count = "PREFIX :     <http://dbpedia.org/resource/> \
                 PREFIX dbo:     <http://dbpedia.org/ontology/> \
                 PREFIX dbp:     <http://dbpedia.org/property/> \
                 SELECT DISTINCT COUNT(?s1) as ?count FROM <http://dbpedia.org> WHERE  { \
                 ?s1 ?p1 %s  . \
                 FILTER(?p1 NOT IN (dbo:wikiPageDisambiguates, dbp:wikiPageUsesTemplate, dbo:wikiPageRedirects)) \
                 FILTER(STRSTARTS(STR(?s1), 'http://dbpedia.org/resource/')) \
                 }";

    #Funcion Vecinos
    fun_neigh = "PREFIX :     <http://dbpedia.org/resource/> \
                 PREFIX dbo:     <http://dbpedia.org/ontology/> \
                 PREFIX dbp:     <http://dbpedia.org/property/> \
                 SELECT  ?p1 ?o1 FROM <http://dbpedia.org> WHERE  { \
                 %s ?p1  ?o1. \
                 FILTER(?p1 NOT IN (dbo:wikiPageDisambiguates, dbp:wikiPageUsesTemplate, dbo:wikiPageRedirects)) \
                 FILTER(STRSTARTS(STR(?o1), 'http://dbpedia.org/resource/')) \
                 }";

    #Funcion Vecinos Count properties
    fun_neigh_count = "PREFIX :     <http://dbpedia.org/resource/> \
                 PREFIX dbo:     <http://dbpedia.org/ontology/> \
                 PREFIX dbp:     <http://dbpedia.org/property/> \
                 SELECT DISTINCT COUNT({conceitoC}) as ?count FROM <http://dbpedia.org> WHERE  {{ \
                 {conceitoC} ?p1 {conceitoAB}  . \
                 FILTER(?p1 NOT IN (dbo:wikiPageDisambiguates, dbp:wikiPageUsesTemplate, dbo:wikiPageRedirects)) \
                 }}";

    #Funcion Resolve Redirects
    fun_redirect = "PREFIX :     <http://dbpedia.org/resource/> \
                 PREFIX dbo:     <http://dbpedia.org/ontology/> \
                 PREFIX dbp:     <http://dbpedia.org/property/> \
                 SELECT  DISTINCT ?o1 FROM <http://dbpedia.org> WHERE  { \
                 %s dbo:wikiPageRedirects ?o1. \
                 FILTER(STRSTARTS(STR(?o1), 'http://dbpedia.org/resource/')) \
                 }";
    #DF da propriedade
    fun_conc_prop_count = "PREFIX :     <http://dbpedia.org/resource/> \
                        PREFIX dbo:     <http://dbpedia.org/ontology/> \
                        PREFIX dbp:     <http://dbpedia.org/property/> \
                        SELECT DISTINCT COUNT({prop}) as ?count FROM <http://dbpedia.org> \
                        WHERE  {{ \
                            ?s1 {prop}  ?o1 .   \
                        }}";
    #Funcion  count prop conc conta quantas vezes esta relação %r aparece apontando pro o conceito %s 
    #TF da propriedade apontando pra A por exemplo
    #aqui to contando quantas vezes a propriedade aparece no grafo ligado ao conceito em questao
    fun_prop_conc_count = "PREFIX :     <http://dbpedia.org/resource/> \
                        PREFIX dbo:     <http://dbpedia.org/ontology/>                  \
                        PREFIX dbp:     <http://dbpedia.org/property/>                  \
                        SELECT DISTINCT COUNT(?s1) as ?count FROM <http://dbpedia.org> \
                        WHERE  {{\
                        ?s1 {prop}  {conceito} .                  \
                        FILTER(STRSTARTS(STR(?s1), 'http://dbpedia.org/resource/'))\
                        }}";

    fun_abstract = "PREFIX :     <http://dbpedia.org/resource/> \
                        PREFIX dbo:     <http://dbpedia.org/ontology/>                  \
                        PREFIX dbp:     <http://dbpedia.org/property/>                  \
                        select ?p FROM <http://dbpedia.org> \
                        WHERE  {\
                        %s dbo:abstract ?abstract .                  \
                        filter(langMatches(lang(?abstract),\"en\"))\
                        BIND( REPLACE( STR(?abstract ),'\"',' ' ) AS ?q).\
                        BIND( REPLACE( STR(?q ),'\\\\+', ' ' ) AS ?r).\
                        BIND( REPLACE( STR(?r ),'\\\\#', ' ' ) AS ?o).\
                        BIND( REPLACE( STR(?o ),'\\r', ' ' ) AS ?m).\
                        BIND( REPLACE( STR(?m ),'\\t', ' ' ) AS ?n).\
                        BIND( REPLACE( STR(?n ),'\\n', ' ' ) AS ?p).\
                        }";

    fun_neigh_count_vazio = "PREFIX :     <http://dbpedia.org/resource/> \
                 PREFIX dbo:     <http://dbpedia.org/ontology/> \
                 PREFIX dbp:     <http://dbpedia.org/property/> \
                 SELECT DISTINCT COUNT(?o1) as ?count FROM <http://dbpedia.org> WHERE  {{ \
                 {conceitoC} ?p1 ?o1 . \
                 FILTER(?p1 NOT IN (dbo:wikiPageDisambiguates, dbp:wikiPageUsesTemplate, dbo:wikiPageRedirects)) \
                 FILTER(STRSTARTS(STR(?o1), 'http://dbpedia.org/resource/')) \
                 }}";

    df_dict = {} #Guardar o df de cada conceito para reduzir a complexidade
    abstract_dict = {} #Guardar o df de cada conceito para reduzir a complexidade

    nlp = spacy.load('en_vectors_web_lg')
    #nlp = spacy.load('en')

    
    DBpediaInstances2016 = 8354799.0 # amazon
    DBpediaInstances2016 = 4678230.0 # colombia
    # SELECT  (COUNT(DISTINCT ?o) AS ?cnt)
    # FROM <http://dbpedia.org>
    # WHERE
    #   { ?s ?p ?o}

    # temos esse select pra todas as instancias no meu grafo
    # select ( count(?s) as ?count )
    # FROM <http://dbpedia.org>
    # where
    # {
    #           ?s rdf:type owl:Thing.
    # } = 8354799 
    # esse select do ruben retorna 5109890
    # o meu retorna = 
    # dbpedia aberta retorna = 5044220;



    # Usar a seguinte SPARQL para contar o total de propriedades da dbpedia
    # SELECT  (COUNT(DISTINCT ?p) AS ?cnt)
    #FROM <http://dbpedia.org>
    # WHERE
    # { ?s ?p ?o}
    DBpediaProperties2016_10 = 65394.0 #resultado do ruben
    #DBpediaProperties2016_10 = 1.0 #resultado da dbpedia aberta
    DBpediaProperties2016_10 = 122959.0 #resultado do meu

    def __init__(self, iconcepta = '', iconceptb= '', icapturaIndica = 'S'):
        """ Constructor """
        self.concepta = iconcepta
        self.conceptb = iconceptb
        self.capturaIndica = icapturaIndica
        config = configparser.ConfigParser()
        config.read('config.cfg')
        self.virtuoso = config.get('Virtuoso4', 'endpoint')
        self.indiConcepta = [] #Guarda os recursos que apontam para o conceito a
        self.indiConceptb = [] #Guarda os recursos que apontam para o conceito b

        self.neighConcepta = [] #Guarda os recursos que apontam para o conceito A com a propriedade pela qual se recuperou o conceito A
        self.neighConceptb = [] #Guarda os recursos que apontam para o conceito B com a propriedade pela qual se recuperou o conceito B
        self.dicPropNeighConceitoA = {}
        self.dictTFPropConceitoA = {}
        self.dicPropNeighConceitoB = {}
        self.dictTFPropConceitoB = {}
        self.dictDFProp = {}

        self.emComumIndB_NeighA = []
        self.emComumIndA_NeighB = []
        self.emComumNeighB_NeighB = []
        self.emComumNeighA_NeighA = []

        self.dictTFConceitoA = {}
        self.dictTFConceitoB = {}
        if self.capturaIndica == 'S':
            self.capturarIndicadores()
            self.emComumIndB_NeighA = list(set(self.indiConceptb).intersection(self.neighConcepta))
            self.emComumIndA_NeighB = list(set(self.indiConcepta).intersection(self.neighConceptb))
            self.emComumNeighA_NeighA = list(set(self.neighConcepta))
            self.emComumNeighB_NeighB = list(set(self.neighConceptb))


    def capturarIndicadores(self):
        
        #consultainidi = self.fun_indi % (self.limpiaRecursos("Africa"))
        consultainidi = self.fun_indi % (self.limpiaRecursos(self.concepta))
        resultoCC=self.consulta(consultainidi)
        for resul in resultoCC['results']['bindings']:

            recurso = resul['s1']['value']
            self.indiConcepta.append(recurso)

        #print("chegou aqui1")
        consultaneight = self.fun_neigh % (self.limpiaRecursos(self.concepta))
        #print(consultaneight)
        resultoCC=self.consulta(consultaneight)
        for resul in resultoCC['results']['bindings']:
            recurso = resul['o1']['value']
            prop = resul['p1']['value']
            self.neighConcepta.append(recurso)
            #aqui eu vou guardar a propriedade p1 que A está ligada no ci:
            self.dicPropNeighConceitoA[recurso] = prop
            #self.propNeighConcepta.append(prop)

        consultainidi = self.fun_indi % (self.limpiaRecursos(self.conceptb))
        #print(consultainidi)
        resultoCC=self.consulta(consultainidi)
        for resul in resultoCC['results']['bindings']:
            #print("chegou aqui2.7")
            #print(resul)
            recurso = resul['s1']['value']
            self.indiConceptb.append(recurso)
        consultaneight = self.fun_neigh % (self.limpiaRecursos(self.conceptb))
        resultoCC=self.consulta(consultaneight)
        for resul in resultoCC['results']['bindings']:
            recurso = resul['o1']['value']
            prop = resul['p1']['value']
            self.neighConceptb.append(recurso)
            #aqui eu vou guardar a propriedade p1 que B está ligada no ci:
            self.dicPropNeighConceitoB[recurso] = prop
        #Despues de recolver los redirects pueden existir duplicados en INDIS
        self.indiConcepta = list(set(self.indiConcepta))
        self.indiConceptb = list(set(self.indiConceptb))

        if not self.indiConcepta:
            raise ValueError("Error: Indi lista vazia para conceito A=" + self.concepta)

        if not self.indiConceptb:
            raise ValueError("Error: Indi lista vazia para conceito B=" + self.conceptb)

        if not self.neighConcepta:
            raise ValueError("Error: Neigh lista vazia para conceito A=" + self.concepta)

        if not self.neighConceptb:
            raise ValueError("Error: Neigh lista vazia para conceito B=" + self.conceptb)

    def calculaRefD_Similar(self):
        somaN1 = 0.0
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.concepta)
                somaN1 += sim
        sim = 0.0
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.conceptb)
                somaN2 += sim
        sim = 0.0
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            if concept in self.neighConcepta:
                sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.concepta)
                somaD1 += sim

        sim = 0.0
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            if concept in self.neighConceptb:
                sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.conceptb)
                somaD2 += sim

        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_Similar_PosCorte(self,novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB):
        somaN1 = 0.0
        for concept in list(set(novaListaComumIndB_NeighA)): #eliminando os repetidos, pois posso ter adicionado o mesmo conceito mais de 1 vez, porem só preciso calcular tf e df uma vez pra ele
            sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.concepta)
            somaN1 += sim
        sim = 0.0
        somaN2 = 0.0
        
        for concept in list(set(novaListaComumIndA_NeighB)):
            sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.conceptb)
            somaN2 += sim
        sim = 0.0
        somaD1 = 0.0
        for concept in novaListaComum_NeighA:
            sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.concepta)
            somaD1 += sim

        sim = 0.0
        somaD2 = 0.0
        for concept in novaListaComum_NeighB:
            sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.conceptb)
            somaD2 += sim

        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_Similar_PosCorteErrado(self,treshold,novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB):
        somaN1 = 0.0
        for concept in list(set(novaListaComumIndB_NeighA)): #eliminando os repetidos, pois posso ter adicionado o mesmo conceito mais de 1 vez, porem só preciso calcular tf e df uma vez pra ele
            sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.concepta)
            if sim >= treshold:
                somaN1 += sim
        sim = 0.0
        somaN2 = 0.0
        
        for concept in list(set(novaListaComumIndA_NeighB)):
            sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.conceptb)
            if sim >= treshold:
                somaN2 += sim
        sim = 0.0
        somaD1 = 0.0
        for concept in novaListaComum_NeighA:
            sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.concepta)
            if sim >= treshold:
                somaD1 += sim

        sim = 0.0
        somaD2 = 0.0
        for concept in novaListaComum_NeighB:
            sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.conceptb)
            if sim >= treshold:
                somaD2 += sim

        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_Similar_CorteSimilar(self,treshold):
        somaN1 = 0.0
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.concepta)
                if sim >= treshold:
                    somaN1 += sim
        sim = 0.0
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.conceptb)
                if sim >= treshold:
                    somaN2 += sim
        sim = 0.0
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            if concept in self.neighConcepta:
                sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.concepta)
                if sim >= treshold:
                    somaD1 += sim

        sim = 0.0
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            if concept in self.neighConceptb:
                sim = self.similaridade(concept.replace('http://dbpedia.org/resource/',' ').strip(),self.conceptb)
                if sim >= treshold:
                    somaD2 += sim

        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_SimilarRecurso(self):
        somaN1 = 0.0
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                simRec = self.similaridadeRecurso(concept.replace("http://dbpedia.org/resource/",""),self.concepta)
                somaN1 += simRec
        simRec = 0.0
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                simRec = self.similaridadeRecurso(concept.replace("http://dbpedia.org/resource/",""),self.conceptb)
                somaN2 += simRec
        simRec = 0.0
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            if concept in self.neighConcepta:
                simRec = self.similaridadeRecurso(concept.replace("http://dbpedia.org/resource/",""),self.concepta)
                somaD1 += simRec

        simRec = 0.0
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            if concept in self.neighConceptb:
                simRec = self.similaridadeRecurso(concept.replace("http://dbpedia.org/resource/",""),self.conceptb)
                somaD2 += simRec

        return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_CossenoWikipedia(self):
        somaN1 = 0.0
        conceitoA = "https://en.wikipedia.org/wiki/" + self.concepta
        conceitoB = "https://en.wikipedia.org/wiki/" + self.conceptb
        print(conceitoA)
        print(conceitoB)
        listaVecConceitoA = self.getListaVecCategFingerPrint(conceitoA)
        listaVecConceitoB = self.getListaVecCategFingerPrint(conceitoB)
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','https://en.wikipedia.org/wiki/')
                #print(c1)
                cos = self.calcCossenoWikipedia(c1,listaVecConceitoA)
                #print(cos)
                somaN1 += cos 
        print("aqui1")
        cos = 0.0
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','https://en.wikipedia.org/wiki/')
                cos = self.calcCossenoWikipedia(c1,listaVecConceitoB)
                somaN2 += cos
        print("aqui2")
        cos = 0.0
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','https://en.wikipedia.org/wiki/')
                print(c1)
                cos = self.calcCossenoWikipedia(c1,listaVecConceitoA)
                print(cos)
                somaD1 += cos
        print("aqui3")
        cos = 0.0
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','https://en.wikipedia.org/wiki/')
                cos = self.calcCossenoWikipedia(c1,listaVecConceitoB)
                somaD2 += cos
        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def salvaAbsAbstract(self,nomeDataset,thresholdAvaliacao):
        abstractconceitoA = ""
        abstractconceitoB = ""
        abstractconceito = ""
        listaComumIndiBNeighA = []
        listaAbstractComumIndiBNeighA = []
        listaComumIndiANeighB = []
        listaAbstractComumIndiANeighB = []
        listaComumNeighA = []
        listaAbstractComumNeighA = []
        listaComumNeighB =[]
        listaAbstractComumNeighB = []
        consultaAbstract = self.fun_abstract % (self.limpiaRecursos(self.concepta))
        #print(consultaAbstract)
        resultoCC=self.consulta(consultaAbstract)
        #print(resultoCC)
        for resul in resultoCC['results']['bindings']:
            abstractconceitoA = resul['p']['value']

        consultaAbstract = self.fun_abstract % (self.limpiaRecursos(self.conceptb))
        #print(consultaAbstract)
        resultoCC=self.consulta(consultaAbstract)
        for resul in resultoCC['results']['bindings']:
            abstractconceitoB = resul['p']['value']
        #print("resumoA = " + abstractconceitoA)
        #print("resumoB = " + abstractconceitoB)
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                listaComumIndiBNeighA.append(concept)
                #print(concept)
                if concept not in self.abstract_dict:
                    consultaAbstract = self.fun_abstract % (self.limpiaRecursos(concept))
                    #print(consultaAbstract)
                    resultoCC=self.consulta(consultaAbstract)
                    for resul in resultoCC['results']['bindings']:
                        abstractconceito = resul['p']['value']
                    self.abstract_dict[concept] = abstractconceito 
                else:
                    abstractconceito = self.abstract_dict[concept]
                listaAbstractComumIndiBNeighA.append(abstractconceito)
                abstractconceito = ""
        abstractconceito = ""
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                listaComumIndiANeighB.append(concept)
                if concept not in self.abstract_dict:
                    consultaAbstract = self.fun_abstract % (self.limpiaRecursos(concept))
                    #print(consultaAbstract)
                    resultoCC=self.consulta(consultaAbstract)
                    for resul in resultoCC['results']['bindings']:
                        abstractconceito = resul['p']['value']
                    self.abstract_dict[concept] = abstractconceito 
                else:
                    abstractconceito = self.abstract_dict[concept]
                listaAbstractComumIndiANeighB.append(abstractconceito)
                abstractconceito = ""
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            if concept in self.neighConcepta:
                listaComumNeighA.append(concept)
                if concept not in self.abstract_dict:    
                    consultaAbstract = self.fun_abstract % (self.limpiaRecursos(concept))
                    #print(consultaAbstract)
                    resultoCC=self.consulta(consultaAbstract)
                    for resul in resultoCC['results']['bindings']:
                        abstractconceito = resul['p']['value']
                    self.abstract_dict[concept] = abstractconceito 
                else:
                    abstractconceito = self.abstract_dict[concept]
                listaAbstractComumNeighA.append(abstractconceito)
                abstractconceito = ""
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            if concept in self.neighConceptb:
                listaComumNeighB.append(concept)
                if concept not in self.abstract_dict:
                    consultaAbstract = self.fun_abstract % (self.limpiaRecursos(concept))
                    #print(consultaAbstract)
                    resultoCC=self.consulta(consultaAbstract)
                    for resul in resultoCC['results']['bindings']:
                        abstractconceito = resul['p']['value']
                    self.abstract_dict[concept] = abstractconceito 
                else:
                    abstractconceito = self.abstract_dict[concept]                        
                listaAbstractComumNeighB.append(abstractconceito)
                abstractconceito = ""
        dict = { 'listaComumIndiBNeighA': listaComumIndiBNeighA, 'listaAbstractComumIndiBNeighA': listaAbstractComumIndiBNeighA}
        df = pandas.DataFrame(dict)
        df.to_csv('./'+str(thresholdAvaliacao)+'/'+nomeDataset+'/output/'+self.concepta +'_' + self.conceptb + '_MLPrerequisite_RefD15_listaComumIndiBNeighA.csv', header=True, index=False)
        dict = { 'listaComumIndiANeighB': listaComumIndiANeighB, 'listaAbstractComumIndiANeighB': listaAbstractComumIndiANeighB}
        df = pandas.DataFrame(dict)
        df.to_csv('./'+str(thresholdAvaliacao)+'/'+nomeDataset+'/output/'+self.concepta +'_' + self.conceptb + '_MLPrerequisite_RefD15_listaComumIndiANeighB.csv', header=True, index=False)
        dict = { 'listaComumNeighA': listaComumNeighA, 'listaAbstractComumNeighA': listaAbstractComumNeighA}
        df = pandas.DataFrame(dict)
        df.to_csv('./'+str(thresholdAvaliacao)+'/'+nomeDataset+'/output/'+self.concepta +'_' + self.conceptb + '_MLPrerequisite_RefD15_listaComumNeighA.csv', header=True, index=False)
        dict = { 'listaComumNeighB': listaComumNeighB, 'listaAbstractComumNeighB': listaAbstractComumNeighB}
        df = pandas.DataFrame(dict)
        df.to_csv('./'+str(thresholdAvaliacao)+'/'+nomeDataset+'/output/'+self.concepta +'_' + self.conceptb + '_MLPrerequisite_RefD15_listaComumNeighB.csv', header=True, index=False)

    def extraiAbstractComArquivoSaida(self,nomeDataset,thresholdAvaliacao):
        abstractconceitoA = ""
        abstractconceitoB = ""

        listaabstractconceitoA = []
        listaabstractconceitoB = []

        consultaAbstract = self.fun_abstract % (self.limpiaRecursos(self.concepta))
        #print(consultaAbstract)
        resultoCC=self.consulta(consultaAbstract)
        #print(resultoCC)
        for resul in resultoCC['results']['bindings']:
            abstractconceitoA = resul['p']['value']
        
        consultaAbstract = self.fun_abstract % (self.limpiaRecursos(self.conceptb))
        #print(consultaAbstract)
        resultoCC=self.consulta(consultaAbstract)
        for resul in resultoCC['results']['bindings']:
            abstractconceitoB = resul['p']['value']
        
        return (abstractconceitoA,abstractconceitoB)

    def calculaRefD_CossenoWikipediaCiAbstract(self,nomeDataset,thresholdAvaliacao,abstractconceitoA,abstractconceitoB):
        somaN1 = 0.0
        abstractconceito = ""

        listaComumIndiBNeighA = []
        listaAbstractComumIndiBNeighA = []
        listaPesoAIndiBNeighA = []
        listaComumIndiANeighB = []
        listaAbstractComumIndiANeighB = []
        listaPesoBIndiANeighB = []
        listaComumNeighA = []
        listaAbstractComumNeighA = []
        listaPesoANeighA = []
        listaComumNeighB =[]
        listaAbstractComumNeighB = []
        listaPesoBNeighB = []
 
        #print("resumoA = " + abstractconceitoA)
        #print("resumoB = " + abstractconceitoB)
        listaVecConceitoA = self.getListaVecCategFingerPrint(abstractconceitoA)
        listaVecConceitoB = self.getListaVecCategFingerPrint(abstractconceitoB)
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:                
                listaComumIndiBNeighA.append(concept)
                #print(abstractconceito)
                #listaAbstractComumIndiBNeighA.append(abstractconceito)
                p1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
                cos = self.calcCossenoWikipediaAbstract(p1,listaVecConceitoA)
                listaPesoAIndiBNeighA.append(cos)
                p1 = ""
                #print(cos)
                somaN1 += cos 
        #print("aqui1")
        cos = 0.0
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                listaComumIndiANeighB.append(concept)
                #listaAbstractComumIndiANeighB.append(abstractconceito)
                p1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
                cos = self.calcCossenoWikipediaAbstract(p1,listaVecConceitoB)
                listaPesoBIndiANeighB.append(cos)
                p1 = ""
                #print(cos)
                somaN2 += cos
        #print("aqui2")
        cos = 0.0
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            if concept in self.neighConcepta:
                listaComumNeighA.append(concept)
                #listaAbstractComumNeighA.append(abstractconceito)
                p1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
                cos = self.calcCossenoWikipediaAbstract(p1,listaVecConceitoA)
                listaPesoANeighA.append(cos)
                p1 = ""
                #print(cos)
                somaD1 += cos
        #print("aqui3")
        cos = 0.0
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            if concept in self.neighConceptb:
                listaComumNeighB.append(concept)
                #listaAbstractComumNeighB.append(abstractconceito)

                p1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
                cos = self.calcCossenoWikipediaAbstract(p1,listaVecConceitoB)
                listaPesoBNeighB.append(cos)
                p1 = ""
                #print(cos)
                somaD2 += cos
        dict = { 'listaComumIndiBNeighA': listaComumIndiBNeighA, 'listaPesoAIndiBNeighA': listaPesoAIndiBNeighA }
        df = pandas.DataFrame(dict)
        df.to_csv('./'+str(thresholdAvaliacao)+'/'+nomeDataset+'/output/'+self.concepta +'_' + self.conceptb + '_MLPrerequisite_'+nomeDataset+'_listaComumIndiBNeighA_SemAbstract.csv', header=True, index=False)
        dict = { 'listaComumIndiANeighB': listaComumIndiANeighB, 'listaPesoBIndiANeighB': listaPesoBIndiANeighB }
        df = pandas.DataFrame(dict)
        df.to_csv('./'+str(thresholdAvaliacao)+'/'+nomeDataset+'/output/'+self.concepta +'_' + self.conceptb + '_MLPrerequisite_'+nomeDataset+'_listaComumIndiANeighB_SemAbstract.csv', header=True, index=False)
        dict = { 'listaComumNeighA': listaComumNeighA, 'listaPesoANeighA':listaPesoANeighA  }
        df = pandas.DataFrame(dict)
        df.to_csv('./'+str(thresholdAvaliacao)+'/'+nomeDataset+'/output/'+self.concepta +'_' + self.conceptb + '_MLPrerequisite_'+nomeDataset+'_listaComumNeighA_SemAbstract.csv', header=True, index=False)
        dict = { 'listaComumNeighB': listaComumNeighB,'listaPesoBNeighB': listaPesoBNeighB  }
        df = pandas.DataFrame(dict)
        df.to_csv('./'+str(thresholdAvaliacao)+'/'+nomeDataset+'/output/'+self.concepta +'_' + self.conceptb + '_MLPrerequisite_'+nomeDataset+'_listaComumNeighB_SemAbstract.csv', header=True, index=False)
        # print("calculaRefD_CossenoWikipediaAbstract")
        # print(somaN1)
        # print(somaN2)
        # print(somaD1)
        # print(somaD2)

        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_CossenoWikipediaAbstractComArquivoSaida(self,nomeDataset,thresholdAvaliacao):
        somaN1 = 0.0
        abstractconceitoA = ""
        abstractconceitoB = ""
        abstractconceito = ""

        listaComumIndiBNeighA = []
        listaAbstractComumIndiBNeighA = []
        listaPesoAIndiBNeighA = []
        listaComumIndiANeighB = []
        listaAbstractComumIndiANeighB = []
        listaPesoBIndiANeighB = []
        listaComumNeighA = []
        listaAbstractComumNeighA = []
        listaPesoANeighA = []
        listaComumNeighB =[]
        listaAbstractComumNeighB = []
        listaPesoBNeighB = []
        consultaAbstract = self.fun_abstract % (self.limpiaRecursos(self.concepta))
        #print(consultaAbstract)
        resultoCC=self.consulta(consultaAbstract)
        #print(resultoCC)
        for resul in resultoCC['results']['bindings']:
            abstractconceitoA = resul['p']['value']

        consultaAbstract = self.fun_abstract % (self.limpiaRecursos(self.conceptb))
        #print(consultaAbstract)
        resultoCC=self.consulta(consultaAbstract)
        for resul in resultoCC['results']['bindings']:
            abstractconceitoB = resul['p']['value']
        #print("resumoA = " + abstractconceitoA)
        #print("resumoB = " + abstractconceitoB)
        listaVecConceitoA = self.getListaVecCategFingerPrint(abstractconceitoA)
        listaVecConceitoB = self.getListaVecCategFingerPrint(abstractconceitoB)
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                listaComumIndiBNeighA.append(concept)
                if concept not in self.abstract_dict:
                    consultaAbstract = self.fun_abstract % (self.limpiaRecursos(concept))
                    resultoCC=self.consulta(consultaAbstract)
                    for resul in resultoCC['results']['bindings']:
                        abstractconceito = resul['p']['value']
                    self.abstract_dict[concept] = abstractconceito
                else:
                    abstractconceito = self.abstract_dict[concept]
                #print(abstractconceito)
                listaAbstractComumIndiBNeighA.append(abstractconceito)
                cos = self.calcCossenoWikipediaAbstract(abstractconceito,listaVecConceitoA)
                listaPesoAIndiBNeighA.append(cos)
                abstractconceito = ""
                #print(cos)
                somaN1 += cos 
        #print("aqui1")
        cos = 0.0
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                listaComumIndiANeighB.append(concept)
                if concept not in self.abstract_dict:
                    consultaAbstract = self.fun_abstract % (self.limpiaRecursos(concept))
                    resultoCC=self.consulta(consultaAbstract)
                    for resul in resultoCC['results']['bindings']:
                        abstractconceito = resul['p']['value']
                    self.abstract_dict[concept] = abstractconceito
                else:
                    abstractconceito = self.abstract_dict[concept]
                listaAbstractComumIndiANeighB.append(abstractconceito)
                cos = self.calcCossenoWikipediaAbstract(abstractconceito,listaVecConceitoB)
                listaPesoBIndiANeighB.append(cos)
                abstractconceito = ""
                #print(cos)
                somaN2 += cos
        #print("aqui2")
        cos = 0.0
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            if concept in self.neighConcepta:
                listaComumNeighA.append(concept)
                if concept not in self.abstract_dict:
                    consultaAbstract = self.fun_abstract % (self.limpiaRecursos(concept))
                    resultoCC=self.consulta(consultaAbstract)
                    for resul in resultoCC['results']['bindings']:
                        abstractconceito = resul['p']['value']
                    self.abstract_dict[concept] = abstractconceito
                else:
                    abstractconceito = self.abstract_dict[concept]
                listaAbstractComumNeighA.append(abstractconceito)
                cos = self.calcCossenoWikipediaAbstract(abstractconceito,listaVecConceitoA)
                listaPesoANeighA.append(cos)
                abstractconceito = ""
                #print(cos)
                somaD1 += cos
        #print("aqui3")
        cos = 0.0
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            if concept in self.neighConceptb:
                listaComumNeighB.append(concept)
                if concept not in self.abstract_dict:
                    consultaAbstract = self.fun_abstract % (self.limpiaRecursos(concept))
                    resultoCC=self.consulta(consultaAbstract)
                    for resul in resultoCC['results']['bindings']:
                        abstractconceito = resul['p']['value']
                    self.abstract_dict[concept] = abstractconceito
                else:
                    abstractconceito = self.abstract_dict[concept]
                listaAbstractComumNeighB.append(abstractconceito)

                cos = self.calcCossenoWikipediaAbstract(abstractconceito,listaVecConceitoB)
                # if concept=='http://dbpedia.org/resource/IBM_Cognos_Business_Intelligence':
                #     print(abstractconceito)
                #     print(cos)
                listaPesoBNeighB.append(cos)
                abstractconceito = ""
                #print(cos)
                somaD2 += cos
        dict = { 'listaComumIndiBNeighA': listaComumIndiBNeighA, 'listaPesoAIndiBNeighA': listaPesoAIndiBNeighA, 'listaAbstractComumIndiBNeighA': listaAbstractComumIndiBNeighA}
        df = pandas.DataFrame(dict)
        df.to_csv('./'+str(thresholdAvaliacao)+'/'+nomeDataset+'/output/'+self.concepta +'_' + self.conceptb + '_MLPrerequisite_'+nomeDataset+'_listaComumIndiBNeighA.csv', header=True, index=False)
        dict = { 'listaComumIndiANeighB': listaComumIndiANeighB, 'listaPesoBIndiANeighB': listaPesoBIndiANeighB, 'listaAbstractComumIndiANeighB': listaAbstractComumIndiANeighB}
        df = pandas.DataFrame(dict)
        df.to_csv('./'+str(thresholdAvaliacao)+'/'+nomeDataset+'/output/'+self.concepta +'_' + self.conceptb + '_MLPrerequisite_'+nomeDataset+'_listaComumIndiANeighB.csv', header=True, index=False)
        dict = { 'listaComumNeighA': listaComumNeighA, 'listaPesoANeighA':listaPesoANeighA, 'listaAbstractComumNeighA': listaAbstractComumNeighA}
        df = pandas.DataFrame(dict)
        df.to_csv('./'+str(thresholdAvaliacao)+'/'+nomeDataset+'/output/'+self.concepta +'_' + self.conceptb + '_MLPrerequisite_'+nomeDataset+'_listaComumNeighA.csv', header=True, index=False)
        dict = { 'listaComumNeighB': listaComumNeighB,'listaPesoBNeighB': listaPesoBNeighB ,'listaAbstractComumNeighB': listaAbstractComumNeighB}
        df = pandas.DataFrame(dict)
        df.to_csv('./'+str(thresholdAvaliacao)+'/'+nomeDataset+'/output/'+self.concepta +'_' + self.conceptb + '_MLPrerequisite_'+nomeDataset+'_listaComumNeighB.csv', header=True, index=False)
        # print("calculaRefD_CossenoWikipediaAbstract")
        # print(somaN1)
        # print(somaN2)
        # print(somaD1)
        # print(somaD2)

        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_CossenoWikipediaAbstract(self):
        somaN1 = 0.0
        abstractconceitoA = ""
        abstractconceitoB = ""
        abstractconceito = ""
        consultaAbstract = self.fun_abstract % (self.limpiaRecursos(self.concepta))
        #print(consultaAbstract)
        resultoCC=self.consulta(consultaAbstract)
        #print(resultoCC)
        for resul in resultoCC['results']['bindings']:
            abstractconceitoA = resul['p']['value']

        consultaAbstract = self.fun_abstract % (self.limpiaRecursos(self.conceptb))
        #print(consultaAbstract)
        resultoCC=self.consulta(consultaAbstract)
        for resul in resultoCC['results']['bindings']:
            abstractconceitoB = resul['p']['value']
        #print("resumoA = " + abstractconceitoA)
        #print("resumoB = " + abstractconceitoB)
        listaVecConceitoA = self.getListaVecCategFingerPrint(abstractconceitoA)
        listaVecConceitoB = self.getListaVecCategFingerPrint(abstractconceitoB)
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                if concept not in self.abstract_dict:
                    consultaAbstract = self.fun_abstract % (self.limpiaRecursos(concept))
                    resultoCC=self.consulta(consultaAbstract)
                    for resul in resultoCC['results']['bindings']:
                        abstractconceito = resul['p']['value']
                    self.abstract_dict[concept] = abstractconceito
                else:
                    abstractconceito = self.abstract_dict[concept]
                #print(abstractconceito)
                cos = self.calcCossenoWikipediaAbstract(abstractconceito,listaVecConceitoA)
                abstractconceito = ""
                #print(cos)
                somaN1 += cos 
        #print("aqui1")
        cos = 0.0
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                if concept not in self.abstract_dict:
                    consultaAbstract = self.fun_abstract % (self.limpiaRecursos(concept))
                    resultoCC=self.consulta(consultaAbstract)
                    for resul in resultoCC['results']['bindings']:
                        abstractconceito = resul['p']['value']
                    self.abstract_dict[concept] = abstractconceito
                else:
                    abstractconceito = self.abstract_dict[concept]
                cos = self.calcCossenoWikipediaAbstract(abstractconceito,listaVecConceitoB)
                abstractconceito = ""
                #print(cos)
                somaN2 += cos
        #print("aqui2")
        cos = 0.0
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            if concept in self.neighConcepta:
                if concept not in self.abstract_dict:
                    consultaAbstract = self.fun_abstract % (self.limpiaRecursos(concept))
                    resultoCC=self.consulta(consultaAbstract)
                    for resul in resultoCC['results']['bindings']:
                        abstractconceito = resul['p']['value']
                    self.abstract_dict[concept] = abstractconceito
                else:
                    abstractconceito = self.abstract_dict[concept]
                cos = self.calcCossenoWikipediaAbstract(abstractconceito,listaVecConceitoA)
                abstractconceito = ""
                #print(cos)
                somaD1 += cos
        #print("aqui3")
        cos = 0.0
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            if concept in self.neighConceptb:
                if concept not in self.abstract_dict:
                    consultaAbstract = self.fun_abstract % (self.limpiaRecursos(concept))
                    resultoCC=self.consulta(consultaAbstract)
                    for resul in resultoCC['results']['bindings']:
                        abstractconceito = resul['p']['value']
                    self.abstract_dict[concept] = abstractconceito
                else:
                    abstractconceito = self.abstract_dict[concept]
                cos = self.calcCossenoWikipediaAbstract(abstractconceito,listaVecConceitoB)
                abstractconceito = ""
                #print(cos)
                somaD2 += cos
        print("calculaRefD_CossenoWikipediaAbstract")
        print(somaN1)
        print(somaN2)
        print(somaD1)
        print(somaD2)

        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_Levenshtein(self):
        somaN1 = 0.0
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistance(c1,self.concepta)
                somaN1 += lvd
        lvd = 0.0
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistance(c1,self.conceptb)
                somaN2 += lvd
        lvd = 0.0
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistance(c1,self.concepta)
                somaD1 += lvd

        lvd = 0.0
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistance(c1,self.conceptb)
                somaD2 += lvd
        return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_Levenshtein_PosCorteErrado(self, treshold,novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB):
        somaN1 = 0.0
        for concept in list(set(novaListaComumIndB_NeighA)): #eliminando os repetidos, pois posso ter adicionado o mesmo conceito mais de 1 vez, porem só preciso calcular tf e df uma vez pra ele                
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.concepta)
            if lvd <= treshold:
                somaN1 += lvd
        lvd = 0.0
        somaN2 = 0.0
        for concept in list(set(novaListaComumIndA_NeighB)):
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.conceptb)
            if lvd <= treshold:
                somaN2 += lvd
        lvd = 0.0
        somaD1 = 0.0
        for concept in novaListaComum_NeighA: #neighA = recursos ci onde, A aponta para ci w(ci,A)
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.concepta)
            if lvd <= treshold:
                somaD1 += lvd

        lvd = 0.0
        somaD2 = 0.0
        for concept in novaListaComum_NeighB:#neighB = recursos ci onde, B aponta para ci w(ci,B)
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.conceptb)
            if lvd <= treshold:
                somaD2 += lvd

        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_Levenshtein_PosCorte(self,novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB):
        somaN1 = 0.0
        for concept in list(set(novaListaComumIndB_NeighA)): #eliminando os repetidos, pois posso ter adicionado o mesmo conceito mais de 1 vez, porem só preciso calcular tf e df uma vez pra ele                
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.concepta)
            somaN1 += lvd
        lvd = 0.0
        somaN2 = 0.0
        for concept in list(set(novaListaComumIndA_NeighB)):
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.conceptb)
            somaN2 += lvd
        lvd = 0.0
        somaD1 = 0.0
        for concept in novaListaComum_NeighA: #neighA = recursos ci onde, A aponta para ci w(ci,A)
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.concepta)
            somaD1 += lvd

        lvd = 0.0
        somaD2 = 0.0
        for concept in novaListaComum_NeighB:#neighB = recursos ci onde, B aponta para ci w(ci,B)
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.conceptb)
            somaD2 += lvd

        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_LevenshteinNorm(self):
        somaN1 = 0.0
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistanceNorm(c1,self.concepta)
                somaN1 += lvd
        lvd = 0.0
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistanceNorm(c1,self.conceptb)
                somaN2 += lvd
        lvd = 0.0
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistanceNorm(c1,self.concepta)
                somaD1 += lvd

        lvd = 0.0
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistanceNorm(c1,self.conceptb)
                somaD2 += lvd

        return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_LevenshteinNorm_PosCorteErrado(self, treshold,novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB):
        somaN1 = 0.0
        for concept in list(set(novaListaComumIndB_NeighA)): #eliminando os repetidos, pois posso ter adicionado o mesmo conceito mais de 1 vez, porem só preciso calcular tf e df uma vez pra ele                
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.concepta)
            if lvd >= treshold:
                somaN1 += lvd
        lvd = 0.0
        somaN2 = 0.0
        for concept in list(set(novaListaComumIndA_NeighB)):
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.conceptb)
            if lvd >= treshold:
                somaN2 += lvd
        lvd = 0.0
        somaD1 = 0.0
        for concept in novaListaComum_NeighA: #neighA = recursos ci onde, A aponta para ci w(ci,A)
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.concepta)
            if lvd >= treshold:
                somaD1 += lvd

        lvd = 0.0
        somaD2 = 0.0
        for concept in novaListaComum_NeighB:#neighB = recursos ci onde, B aponta para ci w(ci,B)
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.conceptb)
            if lvd >= treshold:
                somaD2 += lvd

        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_LevenshteinNorm_PosCorte(self,novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB):
        somaN1 = 0.0
        for concept in list(set(novaListaComumIndB_NeighA)): #eliminando os repetidos, pois posso ter adicionado o mesmo conceito mais de 1 vez, porem só preciso calcular tf e df uma vez pra ele                
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.concepta)
            somaN1 += lvd
        lvd = 0.0
        somaN2 = 0.0
        for concept in list(set(novaListaComumIndA_NeighB)):
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.conceptb)
            somaN2 += lvd
        lvd = 0.0
        somaD1 = 0.0
        for concept in novaListaComum_NeighA: #neighA = recursos ci onde, A aponta para ci w(ci,A)
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.concepta)
            somaD1 += lvd
        lvd = 0.0
        somaD2 = 0.0
        for concept in novaListaComum_NeighB:#neighB = recursos ci onde, B aponta para ci w(ci,B)
            c1 = concept.replace('http://dbpedia.org/resource/','').strip()
            lvd = self.minimumEditDistance(c1,self.conceptb)
            somaD2 += lvd

        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_Levenshtein_CorteLeven(self, treshold):
        somaN1 = 0.0
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistance(c1,self.concepta)
                if lvd <= treshold:
                    somaN1 += lvd
        lvd = 0.0
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistance(c1,self.conceptb)
                if lvd <= treshold:
                    somaN2 += lvd
        lvd = 0.0
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistance(c1,self.concepta)
                if lvd <= treshold:
                    somaD1 += lvd

        lvd = 0.0
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistance(c1,self.conceptb)
                if lvd <= treshold:
                    somaD2 += lvd

        return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_LevenshteinNorm_CorteLevenNorm(self, treshold):
        somaN1 = 0.0
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistanceNorm(c1,self.concepta)
                if lvd >= treshold:#se o threshold passado for um valor normalizado, entre 0 e 1, 1 representando que é o mesmo conceito, eu vou pegar os mais semelhantes sendo maiores que o limiar
                    somaN1 += lvd
        lvd = 0.0
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistanceNorm(c1,self.conceptb)
                if lvd >= treshold:
                    somaN2 += lvd
        lvd = 0.0
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistanceNorm(c1,self.concepta)
                if lvd >= treshold:
                    somaD1 += lvd

        lvd = 0.0
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','').strip()
                lvd = self.minimumEditDistanceNorm(c1,self.conceptb)
                if lvd >= treshold: 
                    somaD2 += lvd

        return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_Equal(self):
        somaN1 = 0.0
        #indiConceptb sao todos os recursos que apontam para B
        #para cada concept ci que aponta para B = r(ci,B), eu vou contar o equals de ci,A; chegando
        # se ci esta dentro de vizinhos de A, ou seja, A aponta para ci, eu conto 1  -> isso aqui é o w(ci,A)
        for concept in self.indiConceptb: # indiConceptb =  recursos que apontam para o conceito b
            if concept in self.neighConcepta: #o peso aqui indica a relecancia do concept do A para o conceito A, entao tenho q comparar com A pra ver o score semantico
                somaN1 += 1#numero de recursos que apontam para o conceito b  r(ci,B)*w(ci,A)

        somaN2 = 0.0
        #indiConcepta sao todos os recursos que apontam para A
        #para cada concept ci que aponta para A = r(ci,A), eu vou contar o equals de ci,B; 
        # se ci esta dentro de vizinhos de B, ou seja, B aponta para ci, eu conto 1  -> isso aqui é o w(ci,B)
        for concept in self.indiConcepta:# indiConcepta =  recursos que apontam para o conceito a
            if concept in self.neighConceptb:
                somaN2 += 1#numero de recursos que apontam para o conceito a  r(ci,A)*w(ci,B)

        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)): #neighA = recursos ci onde, A aponta para ci w(ci,A)
            #if concept in self.neighConcepta:
            somaD1 += 1#numero de recursos para os quais o conceito a aponta w(ci,A)

        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):#neighB = recursos ci onde, B aponta para ci w(ci,B)
            #if concept in self.neighConceptb:
             somaD2 += 1#numero de recursos para os quais o conceito b aponta w(ci,B)

        #print("equal tradicional rubia")
        #print(somaN1)
        #print(somaN2)
        #print(somaD1)
        #print(somaD2)
        # self.emComumIndB_NeighA = list(set(self.indiConceptb).intersection(self.neighConcepta))
        # self.emComumIndA_NeighB = list(set(self.indiConcepta).intersection(self.neighConceptb))
        # self.emComumNeighA_NeighA = list(set(self.neighConcepta))
        # self.emComumNeighB_NeighB = list(set(self.neighConceptb))
        return ((somaN1/somaD1) - (somaN2/somaD2))

    def Calculadf(self, conceptC):
        if conceptC not in self.df_dict:
            consultadf = self.fun_indi_count % (self.limpiaRecursos(conceptC))
            #print(consultadf)
            resultoCC=self.consulta(consultadf)
            for resul in resultoCC['results']['bindings']:
                df = float(resul['count']['value']) + 1 # The number of Wikipedia articles where the concept C appears= Los recursos que tienen un enlace al concepto C mas el articulo del concepto mismo
            self.df_dict[conceptC] = df
        else:
            df = self.df_dict[conceptC]

        return df

    def calculaRefD_tfidf(self):
        somaN1 = 0.0
        for concept in self.indiConceptb:
            tf = self.neighConcepta.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaN1" + concept + str(tf))            
            if tf != 0:
                df = self.Calculadf(concept)
                somaN1 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy1")
        somaN2 = 0.0
        for concept in self.indiConcepta:
            tf = self.neighConceptb.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaN2" + concept + str(tf))            
            if tf != 0:
                df = self.Calculadf(concept)
                somaN2 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy2")
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)):
            tf = self.neighConcepta.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaD1" + concept + str(tf))
            if tf != 0:
                df = self.Calculadf(concept)
                somaD1 += (tf * math.log(self.DBpediaInstances2016/df))

        tf = 0.0
        df = 0.0
        #print("chegeu aquy3")
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):
            tf = self.neighConceptb.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaD2" + concept + str(tf))            
            if tf != 0:
                df = self.Calculadf(concept)
                somaD2 += (tf * math.log(self.DBpediaInstances2016/df))
        #print("tfidf tradicional")
        #print(somaN1)
        #print(somaN2)
        #print(somaD1)
        #print(somaD2)
        return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_Equal_PosCorte(self,novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB):
        somaN1 = 0.0
        #indiConceptb sao todos os recursos que apontam para B
        #para cada concept ci que aponta para B = r(ci,B), eu vou contar o equals de ci,A; chegando
        # se ci esta dentro de vizinhos de A, ou seja, A aponta para ci, eu conto 1  -> isso aqui é o w(ci,A)
        for concept in list(set(novaListaComumIndB_NeighA)): 
            somaN1 += 1
        somaN2 = 0.0
        #indiConcepta sao todos os recursos que apontam para A
        #para cada concept ci que aponta para A = r(ci,A), eu vou contar o equals de ci,B; 
        # se ci esta dentro de vizinhos de B, ou seja, B aponta para ci, eu conto 1  -> isso aqui é o w(ci,B)
        for concept in list(set(novaListaComumIndA_NeighB)):
            somaN2 += 1
        somaD1 = 0.0
        for concept in list(set(novaListaComum_NeighA)):
            #if concept in self.neighConcepta:
            somaD1 += 1
        somaD2 = 0.0
        for concept in list(set(novaListaComum_NeighB)):
            #if concept in self.neighConceptb:
             somaD2 += 1
        #print("equal tradicional rubia")
        #print(somaN1)
        #print(somaN2)
        #print(somaD1)
        #print(somaD2)
        # self.emComumIndB_NeighA = list(set(self.indiConceptb).intersection(self.neighConcepta))
        # self.emComumIndA_NeighB = list(set(self.indiConcepta).intersection(self.neighConceptb))
        # self.emComumNeighA_NeighA = list(set(self.neighConcepta))
        # self.emComumNeighB_NeighB = list(set(self.neighConceptb))
        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_tfidf_Prop_PosCorte(self,novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB):
        somaN1 = 0.0
        tf = 0.0
        df = 0.0
        for concept in list(set(novaListaComumIndB_NeighA)): 
            prop = self.dicPropNeighConceitoA[concept]
            tf = self.calculaTF_PropConceitoA(prop)
            if tf != 0:
                df = self.calculaDF_Prop(prop)
                somaN1 += (tf * math.log(self.DBpediaProperties2016_10/df))
        tf = 0.0
        df = 0.0
        #print("chegou aqui1")
        somaN2 = 0.0
        for concept in list(set(novaListaComumIndA_NeighB)):
            prop = self.dicPropNeighConceitoB[concept]
            tf = self.calculaTF_PropConceitoB(prop)
            if tf != 0:
                df = self.calculaDF_Prop(prop)
                somaN2 += (tf * math.log(self.DBpediaProperties2016_10/df))
        tf = 0.0
        df = 0.0
       # print("chegou aqui2")
        somaD1 = 0.0
        for concept in list(set(novaListaComum_NeighA)):
            prop = self.dicPropNeighConceitoA[concept]
            tf = self.calculaTF_PropConceitoA(prop)
            if tf != 0:
                df = self.calculaDF_Prop(prop)
                # print(type(df))
                # print(df)
                # print(type(tf))
                # print(tf)
                # print(type(self.DBpediaInstances2016))
                somaD1 += (tf * math.log(self.DBpediaProperties2016_10/df))

        tf = 0.0
        df = 0.0
        #print("chegou aqui3")
        somaD2 = 0.0
        for concept in list(set(novaListaComum_NeighB)):
            prop = self.dicPropNeighConceitoB[concept]
            tf = self.calculaTF_PropConceitoB(prop)
            if tf != 0:
                df = self.calculaDF_Prop(prop)
                somaD2 += (tf * math.log(self.DBpediaProperties2016_10/df))
        #print("tfidf propriedades")
        #print(somaN1)
        #print(somaN2)
        #print(somaD1)
        #print(somaD2)
        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_tfidf_PosCorte(self,novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB):
        somaN1 = 0.0
        #aqui faz o calculo tf-idf
        for concept in list(set(novaListaComumIndB_NeighA)): #eliminando os repetidos, pois posso ter adicionado o mesmo conceito mais de 1 vez, porem só preciso calcular tf e df uma vez pra ele
            tf = novaListaComumIndB_NeighA.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaN1" + concept + str(tf))            
            if tf != 0:
                df = self.Calculadf(concept)
                somaN1 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy1")
        somaN2 = 0.0
        #aqui faz o calculo tf-idf
        for concept in list(set(novaListaComumIndA_NeighB)):
            tf = novaListaComumIndA_NeighB.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaN1" + concept + str(tf))            
            if tf != 0:
                df = self.Calculadf(concept)
                somaN2 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy2")
        somaD1 = 0.0
        for concept in novaListaComum_NeighA:   
            tf = self.neighConcepta.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaD1" + concept + str(tf))
            if tf != 0:
                df = self.Calculadf(concept)
                somaD1 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy3")
        somaD2 = 0.0
        for concept in novaListaComum_NeighB:
                tf = self.neighConceptb.count(concept)
                #if (tf > 1):
                    #print("tf > 1 - somaD2" + concept + str(tf))            
                if tf != 0:
                    df = self.Calculadf(concept)
                    somaD2 += (tf * math.log(self.DBpediaInstances2016/df))
        #print("tfidf calculaRefD_tfidf_CorteLeven")
        #print(somaN1)
        #print(somaN2)
        #print(somaD1)
        #print(somaD2)
        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    #esse aqui é o peso TF-IDF e o corte Leven
    def calculaRefD_tfidf_CorteLeven(self,treshold):
        somaN1 = 0.0
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','')
                score = self.minimumEditDistance(c1,self.concepta)
                # print(p1)
                # print(score)
                if score >= treshold:
                    tf = self.neighConcepta.count(concept)
                    #if (tf > 1):
                        #print("tf > 1 - somaN1" + concept + str(tf))            
                    if tf != 0:
                        df = self.Calculadf(concept)
                        somaN1 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy1")
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','')
                score = self.minimumEditDistance(c1,self.conceptb)
                #print(p1)
                #print(score)
                if score >= treshold:
                    tf = self.neighConceptb.count(concept)
                    #if (tf > 1):
                        #print("tf > 1 - somaN2" + concept + str(tf))            
                    if tf != 0:
                        df = self.Calculadf(concept)
                        somaN2 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy2")
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)):
            c1 = concept.replace('http://dbpedia.org/resource/','')
            score = self.minimumEditDistance(c1,self.concepta)
            #print(p1)
            #print(score)
            if score >= treshold:
                tf = self.neighConcepta.count(concept)
                #if (tf > 1):
                    #print("tf > 1 - somaD1" + concept + str(tf))
                if tf != 0:
                    df = self.Calculadf(concept)
                    somaD1 += (tf * math.log(self.DBpediaInstances2016/df))

        tf = 0.0
        df = 0.0
        #print("chegeu aquy3")
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):
            c1 = concept.replace('http://dbpedia.org/resource/','')
            score = self.minimumEditDistance(c1,self.conceptb)
            #print(p1)
            #print(score)
            if score >= treshold:
                tf = self.neighConceptb.count(concept)
                #if (tf > 1):
                    #print("tf > 1 - somaD2" + concept + str(tf))            
                if tf != 0:
                    df = self.Calculadf(concept)
                    somaD2 += (tf * math.log(self.DBpediaInstances2016/df))
        #print("tfidf calculaRefD_tfidf_CorteLeven")
        #print(somaN1)
        #print(somaN2)
        #print(somaD1)
        #print(somaD2)
        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

#esse aqui retorna o espaço conceitual de entrada após o corte Leven 
    def retornaConceitosPosCorteLeven(self,treshold):
        somaN1 = 0.0
        novaListaComumIndB_NeighA = []
        novaListaComumIndA_NeighB = []
        novaListaComum_NeighA = []
        novaListaComum_NeighB = []
        #aqui faz só o corte
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','')
                score = self.minimumEditDistance(c1,self.concepta)
                # print(p1)
                # print(score)
                if score <= treshold:
                    novaListaComumIndB_NeighA.append(concept)
        
        #aqui faz só o corte
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','')
                score = self.minimumEditDistance(c1,self.conceptb)
                #print(p1)
                #print(score)
                if score <= treshold:
                    novaListaComumIndA_NeighB.append(concept)

        
        for concept in list(set(self.neighConcepta)):
            c1 = concept.replace('http://dbpedia.org/resource/','')
            score = self.minimumEditDistance(c1,self.concepta)
            #print(p1)
            #print(score)
            if score <= treshold:
                novaListaComum_NeighA.append(concept)

        
        for concept in list(set(self.neighConceptb)):
            c1 = concept.replace('http://dbpedia.org/resource/','')
            score = self.minimumEditDistance(c1,self.conceptb)
            #print(p1)
            #print(score)
            if score <= treshold:
                novaListaComum_NeighB.append(concept)
        # self.emComumIndB_NeighA = list(set(self.indiConceptb).intersection(self.neighConcepta))
        # self.emComumIndA_NeighB = list(set(self.indiConcepta).intersection(self.neighConceptb))
        # self.emComumNeighA_NeighA = list(set(self.neighConcepta))
        # self.emComumNeighB_NeighB = list(set(self.neighConceptb))
        retorno = (novaListaComumIndB_NeighA, novaListaComumIndA_NeighB, novaListaComum_NeighA, novaListaComum_NeighB)
        return retorno

#esse aqui retorna o espaço conceitual de entrada após o corte Leven 
    def retornaConceitosPosCorteLevenInvertido(self,treshold):
        somaN1 = 0.0
        novaListaComumIndB_NeighA = []
        novaListaComumIndA_NeighB = []
        novaListaComum_NeighA = []
        novaListaComum_NeighB = []
        #aqui faz só o corte
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','')
                score = self.minimumEditDistance(c1,self.concepta)
                # print(p1)
                # print(score)
                if score >= treshold:
                    novaListaComumIndB_NeighA.append(concept)
        
        #aqui faz só o corte
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','')
                score = self.minimumEditDistance(c1,self.conceptb)
                #print(p1)
                #print(score)
                if score >= treshold:
                    novaListaComumIndA_NeighB.append(concept)

        
        for concept in list(set(self.neighConcepta)):
            c1 = concept.replace('http://dbpedia.org/resource/','')
            score = self.minimumEditDistance(c1,self.concepta)
            #print(p1)
            #print(score)
            if score >= treshold:
                novaListaComum_NeighA.append(concept)

        
        for concept in list(set(self.neighConceptb)):
            c1 = concept.replace('http://dbpedia.org/resource/','')
            score = self.minimumEditDistance(c1,self.conceptb)
            #print(p1)
            #print(score)
            if score >= treshold:
                novaListaComum_NeighB.append(concept)
        # self.emComumIndB_NeighA = list(set(self.indiConceptb).intersection(self.neighConcepta))
        # self.emComumIndA_NeighB = list(set(self.indiConcepta).intersection(self.neighConceptb))
        # self.emComumNeighA_NeighA = list(set(self.neighConcepta))
        # self.emComumNeighB_NeighB = list(set(self.neighConceptb))
        retorno = (novaListaComumIndB_NeighA, novaListaComumIndA_NeighB, novaListaComum_NeighA, novaListaComum_NeighB)
        return retorno

    #esse aqui retorna o espaço conceitual de entrada após o corte Leven normalizado
    def retornaConceitosPosCorteLevenNorm(self,treshold):
        somaN1 = 0.0
        novaListaComumIndB_NeighA = []
        novaListaComumIndA_NeighB = []
        novaListaComum_NeighA = []
        novaListaComum_NeighB = []
        #aqui faz só o corte
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','')
                score = self.minimumEditDistanceNorm(c1,self.concepta)
                # print(p1)
                # print(score)
                if score >= treshold:
                    novaListaComumIndB_NeighA.append(concept)
        
        #aqui faz só o corte
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','')
                score = self.minimumEditDistanceNorm(c1,self.conceptb)
                #print(p1)
                #print(score)
                if score >= treshold:
                    novaListaComumIndA_NeighB.append(concept)

        
        for concept in list(set(self.neighConcepta)):
            c1 = concept.replace('http://dbpedia.org/resource/','')
            score = self.minimumEditDistanceNorm(c1,self.concepta)
            #print(p1)
            #print(score)
            if score >= treshold:
                novaListaComum_NeighA.append(concept)

        
        for concept in list(set(self.neighConceptb)):
            c1 = concept.replace('http://dbpedia.org/resource/','')
            score = self.minimumEditDistanceNorm(c1,self.conceptb)
            #print(p1)
            #print(score)
            if score >= treshold:
                novaListaComum_NeighB.append(concept)
        # self.emComumIndB_NeighA = list(set(self.indiConceptb).intersection(self.neighConcepta))
        # self.emComumIndA_NeighB = list(set(self.indiConcepta).intersection(self.neighConceptb))
        # self.emComumNeighA_NeighA = list(set(self.neighConcepta))
        # self.emComumNeighB_NeighB = list(set(self.neighConceptb))
        retorno = (novaListaComumIndB_NeighA, novaListaComumIndA_NeighB, novaListaComum_NeighA, novaListaComum_NeighB)
        return retorno

#esse aqui retorna o espaço conceitual de entrada após o corte Leven normalizado
    def retornaConceitosPosCorteLevenNormInvertido(self,treshold):
        somaN1 = 0.0
        novaListaComumIndB_NeighA = []
        novaListaComumIndA_NeighB = []
        novaListaComum_NeighA = []
        novaListaComum_NeighB = []
        #aqui faz só o corte
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                c1 = concept.replace('http://dbpedia.org/resource/','')
                score = self.minimumEditDistanceNorm(c1,self.concepta)
                # print(p1)
                # print(score)
                if score <= treshold:
                    novaListaComumIndB_NeighA.append(concept)
        
        #aqui faz só o corte
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','')
                score = self.minimumEditDistanceNorm(c1,self.conceptb)
                #print(p1)
                #print(score)
                if score <= treshold:
                    novaListaComumIndA_NeighB.append(concept)

        
        for concept in list(set(self.neighConcepta)):
            c1 = concept.replace('http://dbpedia.org/resource/','')
            score = self.minimumEditDistanceNorm(c1,self.concepta)
            #print(p1)
            #print(score)
            if score <= treshold:
                novaListaComum_NeighA.append(concept)

        
        for concept in list(set(self.neighConceptb)):
            c1 = concept.replace('http://dbpedia.org/resource/','')
            score = self.minimumEditDistanceNorm(c1,self.conceptb)
            #print(p1)
            #print(score)
            if score <= treshold:
                novaListaComum_NeighB.append(concept)
        # self.emComumIndB_NeighA = list(set(self.indiConceptb).intersection(self.neighConcepta))
        # self.emComumIndA_NeighB = list(set(self.indiConcepta).intersection(self.neighConceptb))
        # self.emComumNeighA_NeighA = list(set(self.neighConcepta))
        # self.emComumNeighB_NeighB = list(set(self.neighConceptb))
        retorno = (novaListaComumIndB_NeighA, novaListaComumIndA_NeighB, novaListaComum_NeighA, novaListaComum_NeighB)
        return retorno

    def calculaRefD_tfidf_CorteLevenPosCorte(self,treshold,novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB):
        somaN1 = 0.0
        #aqui faz o calculo tf-idf
        for concept in list(set(novaListaComumIndB_NeighA)): #eliminando os repetidos, pois posso ter adicionado o mesmo conceito mais de 1 vez, porem só preciso calcular tf e df uma vez pra ele
            tf = novaListaComumIndB_NeighA.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaN1" + concept + str(tf))            
            if tf != 0:
                df = self.Calculadf(concept)
                somaN1 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy1")
        somaN2 = 0.0
        #aqui faz o calculo tf-idf
        for concept in list(set(novaListaComumIndA_NeighB)):
            tf = novaListaComumIndA_NeighB.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaN1" + concept + str(tf))            
            if tf != 0:
                df = self.Calculadf(concept)
                somaN2 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy2")
        somaD1 = 0.0
        for concept in novaListaComum_NeighA:   
            tf = self.neighConcepta.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaD1" + concept + str(tf))
            if tf != 0:
                df = self.Calculadf(concept)
                somaD1 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy3")
        somaD2 = 0.0
        for concept in novaListaComum_NeighB:
                tf = self.neighConceptb.count(concept)
                #if (tf > 1):
                    #print("tf > 1 - somaD2" + concept + str(tf))            
                if tf != 0:
                    df = self.Calculadf(concept)
                    somaD2 += (tf * math.log(self.DBpediaInstances2016/df))
        #print("tfidf calculaRefD_tfidf_CorteLeven")
        #print(somaN1)
        #print(somaN2)
        #print(somaD1)
        #print(somaD2)
        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_tfidf_CorteSimilaridade(self,treshold):
        somaN1 = 0.0
        conceitoA = self.concepta.replace('_', ' ')
        conceitoB = self.conceptb.replace('_', ' ')
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                p1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
                score = self.similaridade(p1,conceitoA)
                if score >= treshold:
                    tf = self.neighConcepta.count(concept)
                    #if (tf > 1):
                        #print("tf > 1 - somaN1" + concept + str(tf))            
                    if tf != 0:
                        df = self.Calculadf(concept)
                        somaN1 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy1")
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
                score = self.similaridade(c1,conceitoB)
                if score >= treshold:
                    tf = self.neighConceptb.count(concept)
                    #if (tf > 1):
                        #print("tf > 1 - somaN2" + concept + str(tf))            
                    if tf != 0:
                        df = self.Calculadf(concept)
                        somaN2 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy2")
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)):
            c1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
            score = self.similaridade(c1,conceitoA)
            # print(c1)
            # print(score)
            if score >= treshold:
                tf = self.neighConcepta.count(concept)
                #if (tf > 1):
                    #print("tf > 1 - somaD1" + concept + str(tf))
                if tf != 0:
                    df = self.Calculadf(concept)
                    somaD1 += (tf * math.log(self.DBpediaInstances2016/df))

        tf = 0.0
        df = 0.0
        #print("chegeu aquy3")
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):
            c1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
            score = self.similaridade(c1,conceitoB)
            # print(c1)
            # print(score)
            if score >= treshold:
                tf = self.neighConceptb.count(concept)
                #if (tf > 1):
                    #print("tf > 1 - somaD2" + concept + str(tf))            
                if tf != 0:
                    df = self.Calculadf(concept)
                    somaD2 += (tf * math.log(self.DBpediaInstances2016/df))
        # print("tfidf calculaRefD_tfidf_CorteSimilaridadeRecursoSimilaridade")
        # print(somaN1)
        # print(somaN2)
        # print(somaD1)
        # print(somaD2)
        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def retornaConceitosPosCorteSimilaridade(self,treshold):
        somaN1 = 0.0
        conceitoA = self.concepta.replace('_', ' ')
        conceitoB = self.conceptb.replace('_', ' ')
        novaListaComumIndB_NeighA = []
        novaListaComumIndA_NeighB = []
        novaListaComum_NeighA = []
        novaListaComum_NeighB = []
        #aqui faz só o corte
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                p1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
                score = self.similaridade(p1,conceitoA)
                # print(p1)
                # print(score)
                if score >= treshold:
                    novaListaComumIndB_NeighA.append(concept)
        
        #aqui faz só o corte
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
                score = self.similaridade(c1,conceitoB)
                #print(p1)
                #print(score)
                if score >= treshold:
                    novaListaComumIndA_NeighB.append(concept)

        
        for concept in list(set(self.neighConcepta)):
            c1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
            score = self.similaridade(c1,conceitoA)
            #print(p1)
            #print(score)
            if score >= treshold:
                novaListaComum_NeighA.append(concept)

        
        for concept in list(set(self.neighConceptb)):
            c1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
            score = self.similaridade(c1,conceitoB)
            #print(p1)
            #print(score)
            if score >= treshold:
                novaListaComum_NeighB.append(concept)
        # self.emComumIndB_NeighA = list(set(self.indiConceptb).intersection(self.neighConcepta))
        # self.emComumIndA_NeighB = list(set(self.indiConcepta).intersection(self.neighConceptb))
        # self.emComumNeighA_NeighA = list(set(self.neighConcepta))
        # self.emComumNeighB_NeighB = list(set(self.neighConceptb))
        retorno = (novaListaComumIndB_NeighA, novaListaComumIndA_NeighB, novaListaComum_NeighA, novaListaComum_NeighB)
        return retorno

    def retornaConceitosPosCorteSimilarInvertido(self,treshold):
        somaN1 = 0.0
        conceitoA = self.concepta.replace('_', ' ')
        conceitoB = self.conceptb.replace('_', ' ')
        novaListaComumIndB_NeighA = []
        novaListaComumIndA_NeighB = []
        novaListaComum_NeighA = []
        novaListaComum_NeighB = []
        #aqui faz só o corte
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                p1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
                score = self.similaridade(p1,conceitoA)
                # print(p1)
                # print(score)
                if score <= treshold:
                    novaListaComumIndB_NeighA.append(concept)
        
        #aqui faz só o corte
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                c1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
                score = self.similaridade(c1,conceitoB)
                #print(p1)
                #print(score)
                if score <= treshold:
                    novaListaComumIndA_NeighB.append(concept)

        
        for concept in list(set(self.neighConcepta)):
            c1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
            score = self.similaridade(c1,conceitoA)
            #print(p1)
            #print(score)
            if score <= treshold:
                novaListaComum_NeighA.append(concept)

        
        for concept in list(set(self.neighConceptb)):
            c1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
            score = self.similaridade(c1,conceitoB)
            #print(p1)
            #print(score)
            if score <= treshold:
                novaListaComum_NeighB.append(concept)
        # self.emComumIndB_NeighA = list(set(self.indiConceptb).intersection(self.neighConcepta))
        # self.emComumIndA_NeighB = list(set(self.indiConcepta).intersection(self.neighConceptb))
        # self.emComumNeighA_NeighA = list(set(self.neighConcepta))
        # self.emComumNeighB_NeighB = list(set(self.neighConceptb))
        retorno = (novaListaComumIndB_NeighA, novaListaComumIndA_NeighB, novaListaComum_NeighA, novaListaComum_NeighB)
        return retorno

    def calculaRefD_tfidf_CorteSimilaridadePosCorte(self,treshold,novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB):
        somaN1 = 0.0
        #aqui faz o calculo tf-idf
        for concept in list(set(novaListaComumIndB_NeighA)): #eliminando os repetidos, pois posso ter adicionado o mesmo conceito mais de 1 vez, porem só preciso calcular tf e df uma vez pra ele
            tf = novaListaComumIndB_NeighA.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaN1" + concept + str(tf))            
            if tf != 0:
                df = self.Calculadf(concept)
                somaN1 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy1")
        somaN2 = 0.0
        #aqui faz o calculo tf-idf
        for concept in list(set(novaListaComumIndA_NeighB)):
            tf = novaListaComumIndA_NeighB.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaN1" + concept + str(tf))            
            if tf != 0:
                df = self.Calculadf(concept)
                somaN2 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy2")
        somaD1 = 0.0
        for concept in novaListaComum_NeighA:   
            tf = self.neighConcepta.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaD1" + concept + str(tf))
            if tf != 0:
                df = self.Calculadf(concept)
                somaD1 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy3")
        somaD2 = 0.0
        for concept in novaListaComum_NeighB:
                tf = self.neighConceptb.count(concept)
                #if (tf > 1):
                    #print("tf > 1 - somaD2" + concept + str(tf))            
                if tf != 0:
                    df = self.Calculadf(concept)
                    somaD2 += (tf * math.log(self.DBpediaInstances2016/df))
        #print("tfidf calculaRefD_tfidf_CorteLeven")
        #print(somaN1)
        #print(somaN2)
        #print(somaD1)
        #print(somaD2)
        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_tfidf_CorteSimilaridade_TF_Correto(self,treshold):
        somaN1 = 0.0
        p2 = self.concepta.replace('_', ' ')
        #print(p2)
        listaComum = []
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                p1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
                score = self.similaridade(p1,p2)
                if score >= treshold:
                    listaComum.append(concept)
        for concept in listaComum:
            tf = listaComum.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaN1" + concept + str(tf))            
            if tf != 0:
                df = self.Calculadf(concept)
                somaN1 += (tf * math.log(self.DBpediaInstances2016/df))
        listaComum = []
        tf = 0.0
        df = 0.0
        #print("chegeu aquy1")
        somaN2 = 0.0
        p2 = self.conceptb.replace('_', ' ')
        #print(p2)
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                p1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
                score = self.similaridade(p1,p2)
                if score >= treshold:
                    listaComum.append(concept)

        for concept in listaComum:
            tf = listaComum.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaN2" + concept + str(tf))            
            if tf != 0:
                df = self.Calculadf(concept)
                somaN2 += (tf * math.log(self.DBpediaInstances2016/df))    
        listaComum = []
        tf = 0.0
        df = 0.0
        #print("chegeu aquy2")
        somaD1 = 0.0
        p2 = self.concepta.replace('_', ' ')
        #print(p2)
        for concept in list(set(self.neighConcepta)):
            p1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
            score = self.similaridade(p1,p2)
            # print(p1)
            # print(score)
            if score >= treshold:
                listaComum.append(concept)
        for concept in listaComum:
            tf = listaComum.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaD1" + concept + str(tf))
            if tf != 0:
                df = self.Calculadf(concept)
                somaD1 += (tf * math.log(self.DBpediaInstances2016/df))
        listaComum = []
        tf = 0.0
        df = 0.0
        #print("chegeu aquy3")
        somaD2 = 0.0
        p2 = self.conceptb.replace('_', ' ')
        #print(p2)
        for concept in list(set(self.neighConceptb)):
            p1 = concept.replace('http://dbpedia.org/resource/','').replace('_', ' ')
            score = self.similaridade(p1,p2)
            # print(p1)
            # print(score)
            if score >= treshold:
                listaComum.append(concept)
       
        for concept in listaComum:
            tf = listaComum.count(concept)
            #if (tf > 1):
                #print("tf > 1 - somaD2" + concept + str(tf))            
            if tf != 0:
                df = self.Calculadf(concept)
                somaD2 += (tf * math.log(self.DBpediaInstances2016/df))
        # print("tfidf calculaRefD_tfidf_CorteSimilaridade_TF_Correto")
        # print(somaN1)
        # print(somaN2)
        # print(somaD1)
        # print(somaD2)
        if somaD1 == 0 or somaD2 == 0:
            return -99
        else:
            return ((somaN1/somaD1) - (somaN2/somaD2))

    def calculaRefD_tfidf_CorteSimilaridadeRecurso(self,treshold):
        somaN1 = 0.0
        conceitoA = 'http://dbpedia.org/resource/' + self.concepta
        conceitoB = 'http://dbpedia.org/resource/' + self.conceptb
        # print(conceitoA)
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                score = self.similaridadeRecurso(concept,conceitoA)
                # print(concept)
                # print(score)
                if score >= treshold:
                    tf = self.neighConcepta.count(concept)
                    #if (tf > 1):
                        #print("tf > 1 - somaN1" + concept + str(tf))            
                    if tf != 0:
                        df = self.Calculadf(concept)
                        somaN1 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy1")
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                score = self.similaridadeRecurso(concept,conceitoB)
                # print(concept)
                # print(score)
                if score >= treshold:
                    tf = self.neighConceptb.count(concept)
                    #if (tf > 1):
                        #print("tf > 1 - somaN2" + concept + str(tf))            
                    if tf != 0:
                        df = self.Calculadf(concept)
                        somaN2 += (tf * math.log(self.DBpediaInstances2016/df))
        tf = 0.0
        df = 0.0
        #print("chegeu aquy2")
        somaD1 = 0.0
        #print(conceitoA)
        for concept in list(set(self.neighConcepta)):
            score = self.similaridadeRecurso(concept,conceitoA)
            # print(p1)
            # print(score)
            if score >= treshold:
                tf = self.neighConcepta.count(concept)
                #if (tf > 1):
                    #print("tf > 1 - somaD1" + concept + str(tf))
                if tf != 0:
                    df = self.Calculadf(concept)
                    somaD1 += (tf * math.log(self.DBpediaInstances2016/df))

        tf = 0.0
        df = 0.0
        #print("chegeu aquy3")
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):
            score = self.similaridadeRecurso(concept,conceitoB)
            # print(p1)
            # print(score)
            if score >= treshold:
                tf = self.neighConceptb.count(concept)
                #if (tf > 1):
                    #print("tf > 1 - somaD2" + concept + str(tf))            
                if tf != 0:
                    df = self.Calculadf(concept)
                    somaD2 += (tf * math.log(self.DBpediaInstances2016/df))
        # print("tfidf calculaRefD_tfidf_CorteSimilaridadeRecurso")
        # print(somaN1)
        # print(somaN2)
        # print(somaD1)
        # print(somaD2)
        return ((somaN1/somaD1) - (somaN2/somaD2))


    def calculaVizinhoVazio(self, conceitoC):
        consultaCountVizinho = (self.fun_neigh_count_vazio).format(conceitoC=self.limpiaRecursos(conceitoC)) 
        #print(consultaCountVizinho)
        resultoCC=self.consulta(consultaCountVizinho)
        contaVizinhoVazio = int(resultoCC['results']['bindings'][0]['count']['value'])
        return contaVizinhoVazio

    def retornaConceitoCorreto(self, conceitoC):
        #print(conceitoC)
        recursoCorreto = conceitoC.replace('_',' ').strip()
        if self.calculaVizinhoVazio(conceitoC) == 0:
            consultaRedirectConceito = self.fun_redirect % (self.limpiaRecursos(conceitoC))
            #print(consultaRedirectConceito)
            resultoCC=self.consulta(consultaRedirectConceito)
            listaResult =  resultoCC['results']['bindings']
            if len(listaResult) != 0:
                print("achou redirect")
                recursoCorreto = resultoCC['results']['bindings'][0]['o1']['value']
                print(recursoCorreto)
                if recursoCorreto.len() != 0:
                    recursoCorreto = self.retornaRecursoPuro(recursoCorreto)
                    recursoCorreto = recursoCorreto.replace('_',' ').strip()
        return recursoCorreto

    def calculaTF_PropConceitoA(self, propriedade):
        #print("entrou em calculaTF_PropConceitoA")
        if propriedade not in self.dictTFPropConceitoA:
            #vou contar qtas vezes a prop aponta para o conceito A
            consultatf = (self.fun_prop_conc_count).format(prop="<" + propriedade + ">",conceito=self.limpiaRecursos(self.concepta)) 
            #print(consultadf)
            resultoCC=self.consulta(consultatf)
            tf = float(resultoCC['results']['bindings'][0]['count']['value'])
            self.dictTFPropConceitoA[propriedade] = tf
        else:
            tf = self.dictTFPropConceitoA[propriedade]
        #print("retornou tf em calculaTF_PropConceitoA")
        return tf
    def calculaTF_PropConceitoB(self, propriedade):
        #print("entrou em calculaTF_PropConceitoB")
        if propriedade not in self.dictTFPropConceitoB:
            #vou contar qtas vezes a prop aponta para o conceito A
            consultatf = (self.fun_prop_conc_count).format(prop="<" + propriedade + ">",conceito=self.limpiaRecursos(self.conceptb)) 
            #print(consultadf)
            resultoCC=self.consulta(consultatf)
            tf = float(resultoCC['results']['bindings'][0]['count']['value'])
            self.dictTFPropConceitoB[propriedade] = tf
        else:
            tf = self.dictTFPropConceitoB[propriedade]
        #print("retornou tf em calculaTF_PropConceitoB")
        return tf
    def calculaDF_Prop(self, propriedade):
        #print("entrou em calculaDF_Prop")
        if propriedade not in self.dictDFProp:
            #vou contar qtas vezes a prop existe na dbpedia
            consultadf = (self.fun_conc_prop_count).format(prop="<" + propriedade + ">")
            #print(consultadf)
            resultoCC=self.consulta(consultadf)
            df = float(resultoCC['results']['bindings'][0]['count']['value'])
            self.dictDFProp[propriedade] = df
        else:
            df = self.dictDFProp[propriedade]
        #print("retornou df em calculaDF_Prop")
        return df

    def calculaRefD_tfidf_Prop(self):
        somaN1 = 0.0
        tf = 0.0
        df = 0.0
        for concept in self.indiConceptb:
            if concept in self.neighConcepta:
                prop = self.dicPropNeighConceitoA[concept]
                tf = self.calculaTF_PropConceitoA(prop)
                if tf != 0:
                    df = self.calculaDF_Prop(prop)
                    somaN1 += (tf * math.log(self.DBpediaProperties2016_10/df))
        tf = 0.0
        df = 0.0
        #print("chegou aqui1")
        somaN2 = 0.0
        for concept in self.indiConcepta:
            if concept in self.neighConceptb:
                prop = self.dicPropNeighConceitoB[concept]
                tf = self.calculaTF_PropConceitoB(prop)
                if tf != 0:
                    df = self.calculaDF_Prop(prop)
                    somaN2 += (tf * math.log(self.DBpediaProperties2016_10/df))
        tf = 0.0
        df = 0.0
       # print("chegou aqui2")
        somaD1 = 0.0
        for concept in list(set(self.neighConcepta)):
            if concept in self.neighConcepta:
                prop = self.dicPropNeighConceitoA[concept]
                tf = self.calculaTF_PropConceitoA(prop)
                if tf != 0:
                    df = self.calculaDF_Prop(prop)
                    # print(type(df))
                    # print(df)
                    # print(type(tf))
                    # print(tf)
                    # print(type(self.DBpediaInstances2016))
                    somaD1 += (tf * math.log(self.DBpediaProperties2016_10/df))

        tf = 0.0
        df = 0.0
        #print("chegou aqui3")
        somaD2 = 0.0
        for concept in list(set(self.neighConceptb)):
            if concept in self.neighConceptb:
                prop = self.dicPropNeighConceitoB[concept]
                tf = self.calculaTF_PropConceitoB(prop)
                if tf != 0:
                    df = self.calculaDF_Prop(prop)
                    somaD2 += (tf * math.log(self.DBpediaProperties2016_10/df))
        #print("tfidf propriedades")
        #print(somaN1)
        #print(somaN2)
        #print(somaD1)
        #print(somaD2)
        return ((somaN1/somaD1) - (somaN2/somaD2))



    @retry(Exception, delay=2, tries=-1)
    def consulta(self, sqlQuery):
        """Executa query"""
        sparql = SPARQLWrapper(self.virtuoso)
        sparql.setReturnFormat(JSON)
        sparql.setRequestMethod(URLENCODED)
        #print(sqlQuery)
        sparql.setQuery(sqlQuery)
        results = sparql.query()
        
        results = results.response.read().decode("unicode_escape")
        
        #results.replace('"', '\\"')
        #results.replace('/', '\\/')
        #print(results)
        #results = json.dumps(results)
        results = json.loads(results)
        # print("chegou aqui5")
        # print ("consulta=" + sqlQuery)
        # results = sparql.queryAndConvert()
        # print ("consulta=" + sqlQuery)
        # results = sparql.query()
        # print("chegou aqui6")
        # print(type(results))
        # sresults = str(results)
        # sresults.encode('utf-8')
        # print(sresults)
        # qr = QueryResult(sresults)
        #print(results)
        #results.encode()
        #results.decode("unicode-escape")
        # print("chegou aqui7")
        # results = results.convert()
        # print("chegou aqui7.5")
        #results = qr.convert()
        #results = results.convert()
        # body = results.response.read()
        # fixed_body = body.decode("unicode_escape")
        # from SPARQLWrapper.Wrapper import jsonlayer
        # results = jsonlayer.decode(fixed_body)
        # print("chegou aqui8")
        #print ("vai retornar a consulta=")
        return results

    def limpiaRecursos(self, recursoDirty):
        """Limpia de () las consultas SPARQL"""
        if "http://dbpedia.org/resource" not in recursoDirty:
            recursoDirty = "http://dbpedia.org/resource/" + recursoDirty

        recursoClean = "<" + recursoDirty + ">"
        return recursoClean

    def retornaRecursoPuro(self, recursoNotPuro):
        if "http://dbpedia.org/resource" in recursoNotPuro:
            recursoPuro = recursoPuro.replace('http://dbpedia.org/resource/','').strip()
        else:
            recursoPuro = "http://dbpedia.org/resource/" + recursoDirty
        return recursoPuro
        

    def minimumEditDistance(self,s1,s2):
        if s1 == s2:
            return 0.0
        if len(s1) > len(s2):
            s1,s2 = s2,s1
        distances = range(len(s1) + 1)
        for index2,char2 in enumerate(s2):
            newDistances = [index2+1]
            for index1,char1 in enumerate(s1):
                if char1 == char2:
                    newDistances.append(distances[index1])
                else:
                    newDistances.append(1 + min((distances[index1],
                                                 distances[index1+1],
                                                 newDistances[-1])))
            distances = newDistances
        return distances[-1]

    def minimumEditDistanceNorm(self,s1,s2):
        if s1 == s2:
            return 0.0
        if len(s1) > len(s2):
            s1,s2 = s2,s1
            maiorTam = len(s1)
        else:
            maiorTam = len(s2)
        distances = range(len(s1) + 1)
        for index2,char2 in enumerate(s2):
            newDistances = [index2+1]
            for index1,char1 in enumerate(s1):
                if char1 == char2:
                    newDistances.append(distances[index1])
                else:
                    newDistances.append(1 + min((distances[index1],
                                                 distances[index1+1],
                                                 newDistances[-1])))
            distances = newDistances
        return (1.0-(distances[-1]/maiorTam))

    def similaridade(self,s1,s2):
        if s1 == s2:
            return 0.0
        p1 = s1.replace("_", " ")
        #print(p1)
        p2 = s2.replace("_", " ")
        #print(p2)
        doc1 = self.nlp(p1)
        doc2 = self.nlp(p2)
        score = doc1.similarity(doc2)
        #print(score)
        return score

    def similaridadeRecurso(self,s1,s2):
        sim = EntitySimilarity()
        score = sim.relatedness(s1,s2)
        #print("s1" + s1)
        #print("s2" + s2)
        return score

    def cosineSimilarityManual(self,a,b):
        # a = np.array([1,2,3])
        # b = np.array([1,1,4])
         
        # manually compute cosine similarity
        dot = np.dot(a, b)
        norma = np.linalg.norm(a)
        normb = np.linalg.norm(b)
        cos = dot / (norma * normb)
        return cos

    def getFingerPrint(self,text):
        url = "http://tagtheweb.com.br/wiki/getFingerPrint.php"
        payload = {'text':text, 'language': 'en','normalize': 'true','depth': '0'}
        files = {}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        #print("aqui4")
        now = datetime.now()
        print("antes")
        print (now)
        sleep(4.0)
        response = requests.request('POST', url, headers = headers, data = payload, files = files, allow_redirects=False)
        now = datetime.now()
        print("depois")
        print (now)
        #print(response.text)
        #print("aqui5")
        if response.status_code == 200:
            print("retornou!!")
            print(response.text.encode('utf8'))
            return response.text
            #return response.text.encode('utf8')
        else:
            print("menos 1=" +text)
            print("response.status_code=" +str(response.status_code))
            return -1

    def getListaVecCategFingerPrint(self, url):
        # print("aqui1")
        #print(url)
        fingerPrint = self.getFingerPrint(url)
        #print(fingerPrint)
        print('tipo='+str(type(fingerPrint)))
        lista = []
        if not isinstance(fingerPrint, str):
            print("menos 1=" + str(lista))
            return lista
        else:
            #my_dict = ast.literal_eval(str(fingerPrint))
            my_dict = json.loads(fingerPrint) 

        #print("avaliou string do finger print")
        
        if not isinstance(my_dict, dict):
            return lista
        else:
            #print("vai fazer a lista dos pesos vetor")
            for categ, valor in my_dict.items(): 
                lista.append(valor)
            return lista

    def calcCossenoWikipediaAbstract(self,abstractConceito,listaVecConceito):
        if (abstractConceito == None or abstractConceito == ""):
            listaS1 = []
        else:
            listaS1 = self.getListaVecCategFingerPrint(abstractConceito)
        if len(listaS1) == 0 or len(listaVecConceito) == 0:
            return 0
        else:
            a = np.array(listaS1)
            b = np.array(listaVecConceito)
            co1 = self.cosineSimilarityManual(a,b)
            return co1

    def calcCossenoWikipedia(self,url,listaVecConceito):
        listaS1 = self.getListaVecCategFingerPrint(url)
        if len(listaS1) == 0 or len(listaVecConceito) == 0:
            return 0
        else:
            a = np.array(listaS1)
            b = np.array(listaVecConceito)
            co1 = self.cosineSimilarityManual(a,b)
            return co1