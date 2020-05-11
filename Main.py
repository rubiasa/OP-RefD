# -*- coding: utf-8 -*-
"""
Created on Sep 17 20:04:48 2019

@author: rubiaalmeida

"""
import requests
import json
import time
from OP_RefD import OPRefD
import os
import csv
import pandas
import re
from datetime import datetime
import time

#Deep_learning, Machine_learning
#Deep_learning, Word_embedding
#Computational_complexity_theory, NP-completeness
#Polymorphism_(computer_science), Method_(computer_programming)
#Not a prerequisite:  Association_football, Polymorphism_(computer_science)
#concepta = "Computational_complexity_theory"
#conceptb = "NP-completeness"
def avaliaResult(refD):
    if (refD > thresholdAvaliacao and refD <= 1.0): # do treshold até 1, é pre-requisito, excluindo o treshold
        result = int(1)
    elif (refD >= -thresholdAvaliacao and refD <= thresholdAvaliacao):
        result = int(-1)
    elif (refD >= -1.0 and refD < -thresholdAvaliacao):
        result = int(0)
    else: # aqui vao ser aquelas maior que 1 e menor que -1
        result = int(-2)
    return result

def calculaRefDGeral(nomeArquivoEntrada, nomeArquivoSaida, nomeMetodoCalculo):
    
    tDescontarAcumulado= 0.0
    ehMetodoCorte = False
    tInicial = time.process_time()
    if nomeMetodoCalculo == 'refDCossenoWikipediaAbstract':
        dfRefD15 = pandas.read_csv('./DATASETS2/' + nomeArquivoEntrada, index_col='id')
    else:
        dfRefD15 = pandas.read_csv('./DATASETS/' + nomeArquivoEntrada, index_col='id')
    arqParcial = './output/Parcial_' + str(thresholdAvaliacao) + '_' + nomeArquivoSaida
    print('arq parcial = ' + arqParcial)
    with open(arqParcial, mode='a', newline='') as teste_file:
        teste_file = csv.writer(teste_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        teste_file.writerow(['id','ConceptA','ConceptB_Pre','prerequisite','refDEqual','refDLeven','refDFIDF','refDFIDF_Prop', 'refDSimilar', 'refDSimilarCorteSimilar_','refDLevenCorteLeven_'])
    #data = ['id','ConceptA', 'ConceptB_Pre','refDEqual','refDLeven']
        for i, row in dfRefD15.iterrows():
            conceitoA = row['ConceptA']
            conceitoB = row['ConceptB_Pre']
            
            if nomeMetodoCalculo == 'refDCossenoWikipediaAbstract':
                abstractConceitoA = row['AbstractConceptA']
                abstractConceitoB = row['AbstractConceptB']
            else:
                abstractConceitoA = ""
                abstractConceitoB = ""

            now = datetime.now()
            
            #print (i)
            #print (now)
            ehPrerequisito = row['prerequisite']
            listaId.append(i)
            listaConceitoA.append(conceitoA)
            listaConceitoB.append(conceitoB)
            listaPreRequisito.append(ehPrerequisito)
            conceitoA = conceitoA.replace (" ", "_") 
            conceitoB = conceitoB.replace (" ", "_")
            #print (conceitoA)
            #print (conceitoB)
            redsimpl = OPRefD(conceitoA,conceitoB)
            #print('fez o inicio da classe')
#listaMetodos = ['refDEqual','refDTFIDFNormal','refDLevenPeso','refDTFIDF_Prop','refDSimilarPeso','refDTFIDFCorteLeven_09','refDTFIDFCorteSimilar_04']
            if nomeMetodoCalculo == 'refDEqual':
                refD = redsimpl.calculaRefD_Equal()
            elif nomeMetodoCalculo == 'refDTFIDFNormal':
                refD = redsimpl.calculaRefD_tfidf()
            elif nomeMetodoCalculo == 'refDLevenPeso':
                refD = redsimpl.calculaRefD_Levenshtein()
            elif nomeMetodoCalculo == 'refDLevenNormPeso':
                refD = redsimpl.calculaRefD_LevenshteinNorm()                
            elif nomeMetodoCalculo == 'refDTFIDF_Prop':
                refD = redsimpl.calculaRefD_tfidf_Prop()
            elif nomeMetodoCalculo == 'refDSimilarPeso':
                refD = redsimpl.calculaRefD_Similar()
            elif nomeMetodoCalculo == 'refDTFIDFCorteLeven_'+str(scoreCorteLeven):#peso tfidf e corte leve
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLeven(scoreCorteLeven)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_tfidf_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodoCalculo == 'refDTFIDFCorteLevenNorm_'+str(scoreCorteLevenNorm):#peso tfidf e corte leve
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenNorm(scoreCorteLevenNorm)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_tfidf_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodoCalculo == 'refDTFIDFCorteSimilar_'+str(scoreCorteSimilar):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteSimilaridade(scoreCorteSimilar)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_tfidf_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodoCalculo == 'refDCossenoWikipediaAbstract':
                #abstractConceitoA,abstractConceitoB = redsimpl.extraiAbstractComArquivoSaida(nomePasta,thresholdAvaliacao)
                listaabstractconceitoA.append(abstractConceitoA)
                listaabstractconceitoB.append(abstractConceitoB)
                
                print('thresholdAvaliacao='+str(thresholdAvaliacao))
                print('nomeDataSet='+nomeDataSet + ', nomePasta='+nomePasta)
                #refD = redsimpl.calculaRefD_CossenoWikipediaAbstractComArquivoSaida(nomeDataSet,thresholdAvaliacao)
                refD = redsimpl.calculaRefD_CossenoWikipediaCiAbstract(nomePasta,thresholdAvaliacao,abstractConceitoA,abstractConceitoB)
                #refD = 99;
                #redsimpl.salvaAbsAbstract(nomePasta,thresholdAvaliacao)
                print('refD='+str(refD))
            elif nomeMetodoCalculo == 'refDSimilarCorteSimilar_'+str(scoreCorteSimilar):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteSimilaridade(scoreCorteSimilar)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Similar_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodoCalculo == 'refDLevenCorteLeven_'+str(scoreCorteLeven):#peso leven e corte leve
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLeven(scoreCorteLeven)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Levenshtein_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodoCalculo == 'refDLevenNormCorteLevenNorm_'+str(scoreCorteLevenNorm):#peso leven e corte leve
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenNorm(scoreCorteLevenNorm)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_LevenshteinNorm_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDEqualCorteSimilar_'+str(scoreCorteSimilar):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteSimilaridade(scoreCorteSimilar)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Equal_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDLevenCorteSimilar_'+str(scoreCorteSimilar):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteSimilaridade(scoreCorteSimilar)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Levenshtein_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDLevenNormCorteSimilar_'+str(scoreCorteSimilar):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteSimilaridade(scoreCorteSimilar)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_LevenshteinNorm_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDTFIDF_PropCorteSimilar_'+str(scoreCorteSimilar):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteSimilaridade(scoreCorteSimilar)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_tfidf_Prop_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDEqualCorteLeven_'+str(scoreCorteLeven):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLeven(scoreCorteLeven)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Equal_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDLevenNormCorteLeven_'+str(scoreCorteLeven):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLeven(scoreCorteLeven)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_LevenshteinNorm_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDSimilarCorteLeven_'+str(scoreCorteLeven):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLeven(scoreCorteLeven)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Similar_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDTFIDF_PropCorteLeven_'+str(scoreCorteLeven):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLeven(scoreCorteLeven)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_tfidf_Prop_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDEqualCorteLevenNorm_'+str(scoreCorteLevenNorm):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenNorm(scoreCorteLevenNorm)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Equal_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True               
            elif nomeMetodo == 'refDLevenCorteLevenNorm_'+str(scoreCorteLevenNorm):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenNorm(scoreCorteLevenNorm)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Levenshtein_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDSimilarCorteLevenNorm_'+str(scoreCorteLevenNorm):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenNorm(scoreCorteLevenNorm)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Similar_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDTFIDF_PropCorteLevenNorm_'+str(scoreCorteLevenNorm):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenNorm(scoreCorteLevenNorm)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_tfidf_Prop_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
#invertidos
            elif nomeMetodo == 'refDEqualCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteSimilarInvertido(scoreCorteSimilarInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Equal_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDEqualCorteLevenInvertido_'+str(scoreCorteLevenInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenInvertido(scoreCorteLevenInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Equal_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDEqualCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenNormInvertido(scoreCorteLevenNormInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Equal_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDTFIDFCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteSimilarInvertido(scoreCorteSimilarInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_tfidf_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDTFIDFCorteLevenInvertido_'+str(scoreCorteLevenInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenInvertido(scoreCorteLevenInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_tfidf_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDTFIDFCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenNormInvertido(scoreCorteLevenNormInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_tfidf_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDLevenCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteSimilarInvertido(scoreCorteSimilarInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Levenshtein_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDLevenCorteLevenInvertido_'+str(scoreCorteLevenInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenInvertido(scoreCorteLevenInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Levenshtein_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDLevenCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenNormInvertido(scoreCorteLevenNormInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Levenshtein_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDLevenNormCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteSimilarInvertido(scoreCorteSimilarInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_LevenshteinNorm_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDLevenNormCorteLevenInvertido_'+str(scoreCorteLevenInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenInvertido(scoreCorteLevenInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_LevenshteinNorm_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDLevenNormCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenNormInvertido(scoreCorteLevenNormInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_LevenshteinNorm_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDSimilarCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteSimilarInvertido(scoreCorteSimilarInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Similar_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDSimilarCorteLevenInvertido_'+str(scoreCorteLevenInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenInvertido(scoreCorteLevenInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Similar_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDSimilarCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenNormInvertido(scoreCorteLevenNormInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_Similar_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDTFIDF_PropCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteSimilarInvertido(scoreCorteSimilarInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_tfidf_Prop_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDTFIDF_PropCorteLevenInvertido_'+str(scoreCorteLevenInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenInvertido(scoreCorteLevenInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_tfidf_Prop_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True
            elif nomeMetodo == 'refDTFIDF_PropCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido):
                tInicialCorte = time.process_time()
                listasConceitos = redsimpl.retornaConceitosPosCorteLevenNorm(scoreCorteLevenNormInvertido)
                novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB = listasConceitos
                tFinalCorte = time.process_time()
                tDescontarAcumulado += (tFinalCorte-tInicialCorte)
                refD = redsimpl.calculaRefD_tfidf_Prop_PosCorte(novaListaComumIndB_NeighA,novaListaComumIndA_NeighB,novaListaComum_NeighA,novaListaComum_NeighB)
                ehMetodoCorte = True

            else:
                raise ValueError('RefD nao definido')

            qtdeConceitosAntesCorteComumIndB_NeighA = len(redsimpl.emComumIndB_NeighA)
            qtdeConceitosAntesCorteComumIndA_NeighB = len(redsimpl.emComumIndA_NeighB)
            qtdeConceitosAntesCorteComum_NeighA = len(redsimpl.emComumNeighA_NeighA)
            qtdeConceitosAntesCorteComum_Neighb = len(redsimpl.emComumNeighB_NeighB)
            if (ehMetodoCorte):
                qtdeConceitosPosCorteComumIndB_NeighA = len(novaListaComumIndB_NeighA)
                qtdeConceitosPosCorteComumIndA_NeighB = len(novaListaComumIndA_NeighB)
                qtdeConceitosPosCorteComum_NeighA = len(novaListaComum_NeighA)
                qtdeConceitosPosCorteComum_Neighb = len(novaListaComum_NeighB)
            else:
                qtdeConceitosPosCorteComumIndB_NeighA = qtdeConceitosAntesCorteComumIndB_NeighA
                qtdeConceitosPosCorteComumIndA_NeighB = qtdeConceitosAntesCorteComumIndA_NeighB
                qtdeConceitosPosCorteComum_NeighA = qtdeConceitosAntesCorteComum_NeighA
                qtdeConceitosPosCorteComum_Neighb = qtdeConceitosAntesCorteComum_Neighb
            
            listaRefD.append(refD)
            listaQtdeConceitosAntesCorteComumIndB_NeighA.append(qtdeConceitosAntesCorteComumIndB_NeighA)
            listaQtdeConceitosAntesCorteComumIndA_NeighB.append(qtdeConceitosAntesCorteComumIndA_NeighB)
            listaQtdeConceitosAntesCorteComum_NeighA.append(qtdeConceitosAntesCorteComum_NeighA)
            listaQtdeConceitosAntesCorteComum_Neighb.append(qtdeConceitosAntesCorteComum_Neighb)
            listaQtdeConceitosPosCorteComumIndB_NeighA.append(qtdeConceitosPosCorteComumIndB_NeighA)
            listaQtdeConceitosPosCorteComumIndA_NeighB.append(qtdeConceitosPosCorteComumIndA_NeighB)
            listaQtdeConceitosPosCorteComum_NeighA.append(qtdeConceitosPosCorteComum_NeighA)
            listaQtdeConceitosPosCorteComum_Neighb.append(qtdeConceitosPosCorteComum_Neighb)


            result = avaliaResult(refD)
            listaResult.append(result)
            if nomeMetodoCalculo == 'refDCossenoWikipediaAbstract_34324234234':
                teste_file.writerow([i,conceitoA,conceitoB,ehPrerequisito,refD,result,abstractConceitoA,abstractConceitoB])

            else: 
                teste_file.writerow([i,conceitoA,conceitoB,ehPrerequisito,refD,result])
            print('escreveu no arquivo=' + conceitoA + ' B='+ conceitoB, ', result = ' + str(result))
    
    
    tFinal = time.process_time()

    listaId.append(9997)
    listaConceitoA.append("Hora Inicial")
    listaConceitoB.append("Hora Inicial")
    listaPreRequisito.append("Hora Inicial")
    listaRefD.append("Hora Inicial")
    listaResult.append(tInicial)

    listaQtdeConceitosAntesCorteComumIndB_NeighA.append("Hora Inicial")
    listaQtdeConceitosPosCorteComumIndB_NeighA.append("Hora Inicial")
    listaQtdeConceitosAntesCorteComumIndA_NeighB.append("Hora Inicial")
    listaQtdeConceitosPosCorteComumIndA_NeighB.append("Hora Inicial")
    listaQtdeConceitosAntesCorteComum_NeighA.append("Hora Inicial")
    listaQtdeConceitosPosCorteComum_NeighA.append("Hora Inicial")
    listaQtdeConceitosAntesCorteComum_Neighb.append("Hora Inicial")
    listaQtdeConceitosPosCorteComum_Neighb.append("Hora Inicial")

    listaId.append(9998)
    listaConceitoA.append("Hora Final")
    listaConceitoB.append("Hora Final")
    listaPreRequisito.append("Hora Final")
    listaRefD.append("Hora Final")
    listaResult.append(tFinal)

    listaQtdeConceitosAntesCorteComumIndB_NeighA.append("Hora Final")
    listaQtdeConceitosPosCorteComumIndB_NeighA.append("Hora Final")
    listaQtdeConceitosAntesCorteComumIndA_NeighB.append("Hora Final")
    listaQtdeConceitosPosCorteComumIndA_NeighB.append("Hora Final")
    listaQtdeConceitosAntesCorteComum_NeighA.append("Hora Final")
    listaQtdeConceitosPosCorteComum_NeighA.append("Hora Final")
    listaQtdeConceitosAntesCorteComum_Neighb.append("Hora Final")
    listaQtdeConceitosPosCorteComum_Neighb.append("Hora Final")

    listaId.append(9999)
    listaConceitoA.append("Tempo Decorrido")
    listaConceitoB.append("Tempo Decorrido")
    listaPreRequisito.append("Tempo Decorrido")
    listaRefD.append("Tempo Decorrido")
    if ehMetodoCorte:#nomeMetodoCalculo == 'refDTFIDFCorteLeven_'+str(scoreCorteLeven):
        listaResult.append(tFinal-tInicial-tDescontarAcumulado)
    else:
        listaResult.append(tFinal-tInicial)

    listaQtdeConceitosAntesCorteComumIndB_NeighA.append("Tempo Decorrido")
    listaQtdeConceitosPosCorteComumIndB_NeighA.append("Tempo Decorrido")
    listaQtdeConceitosAntesCorteComumIndA_NeighB.append("Tempo Decorrido")
    listaQtdeConceitosPosCorteComumIndA_NeighB.append("Tempo Decorrido")
    listaQtdeConceitosAntesCorteComum_NeighA.append("Tempo Decorrido")
    listaQtdeConceitosPosCorteComum_NeighA.append("Tempo Decorrido")
    listaQtdeConceitosAntesCorteComum_Neighb.append("Tempo Decorrido")
    listaQtdeConceitosPosCorteComum_Neighb.append("Tempo Decorrido")

    dict = {'id': listaId, 'ConceptA': listaConceitoA, 'ConceptB_Pre': listaConceitoB, 'prerequisite': listaPreRequisito, 'refD': listaRefD, 'Result': listaResult,'QtdeConcAntesIndB_NeighA':listaQtdeConceitosAntesCorteComumIndB_NeighA, 'QtdeConcPosIndB_NeighA':listaQtdeConceitosPosCorteComumIndB_NeighA, 'QtdeConcAntesIndA_NeighB':listaQtdeConceitosAntesCorteComumIndA_NeighB, 'QtdeConcPosIndA_NeighB':listaQtdeConceitosPosCorteComumIndA_NeighB, 'QtdeConcAntes_NeighA':listaQtdeConceitosAntesCorteComum_NeighA, 'QtdeConcPos_NeighA':listaQtdeConceitosPosCorteComum_NeighA, 'QtdeConcAntes_NeighB':listaQtdeConceitosAntesCorteComum_Neighb, 'QtdeConcPos_NeighB':listaQtdeConceitosPosCorteComum_Neighb }
    df = pandas.DataFrame(dict)
    df.to_csv(caminhoSaida + str(thresholdAvaliacao) + '_' + nomeArquivoSaida, header=True, index=False)
    #df.to_csv('./output/' + str(thresholdAvaliacao) + '_' + nomeArquivoSaida, header=True, index=False)

conceptb = "Computational_complexity_theory"
concepta = "NP-completeness"
conceitoA = ""
conceitoB = ""
abstractConceitoA =""
abstractConceitoB =""
thresholdAvaliacao = 0.05

scoreCorteLeven_RefD15_CS = 13
scoreCorteLeven_RefD15_Math = 16
scoreCorteLeven_eaai17 = 19
scoreCorteLevenInvertido_RefD15_CS = 16
scoreCorteLevenInvertido_RefD15_Math = 5
scoreCorteLevenInvertido_eaai17 = 12

scoreCorteSimilar_RefD15_CS = 0.4
scoreCorteSimilar_RefD15_Math = 0.2
scoreCorteSimilar_eaai17 = 0.1
scoreCorteSimilarInvertido_RefD15_CS = 0.9
scoreCorteSimilarInvertido_RefD15_Math = 0.7
scoreCorteSimilarInvertido_eaai17 = 0.6

scoreCorteLevenNorm_RefD15_CS = 0.6
scoreCorteLevenNorm_RefD15_Math = 0.1
scoreCorteLevenNorm_eaai17 = 0.1
scoreCorteLevenNormInvertido_RefD15_CS = 0.4
scoreCorteLevenNormInvertido_RefD15_Math = 0.2
scoreCorteLevenNormInvertido_eaai17 = 0.9

#arquivoSaida = "MLPrerequisite_RefD15_CS_Equal.csv"
#nomeMetodo = 'refDEqual'
#nomeMetodo = 'refDTFIDF'
#nomeMetodo = 'refDLeven'
#nomeMetodo = 'refDTFIDF_Prop'
#nomeMetodo = 'refDSimilar'
#nomeMetodo = 'refDTFIDFCorteLeven_09'
#nomeMetodo = 'refDTFIDFCorteSimilar_04'
#nomeMetodo = 'refDTFIDFCorteLeven_13'
#nomeMetodo = 'refDTFIDFCorteSimilar_03'
#nomeMetodo = 'refDTFIDFCorteLeven_09'
#nomeMetodo = 'refDTFIDFCorteSimilar_02'
nomeMetodo = 'refDCossenoWikipediaAbstract'


nomeDataSet = "eaai17"
nomeDataSet = "RefD15_CS"
nomeDataSet = "RefD15_Math"
listaMetodos = []
try:
    listaDatasets = ['RefD15_Math','RefD15_CS','eaai17']

    listaDatasets = ['RefD15_Math']
    listaDatasets = ['RefD15_CS','eaai17']
    listaDatasets = ['eaai17']
    listaDatasets = ['RefD15_CS']

    listaDatasets = ['RefD15_Math','eaai17']
    nomePasta = ''
    for nomeDataSet in listaDatasets:
        if (nomeDataSet == "RefD15_Math"):
            caminhoSaida = './' + str(thresholdAvaliacao) + '/MATH/' 
            nomePasta = 'MATH'
            arquivoEntrada = "07-07-19-MLPrerequisite_RefD15_Math.csv"
            arquivoEntrada2 = "19-03-20-MLPrerequisite_RefD15_Math.csv"
            #arquivoEntrada2 = "20-03-20-MLPrerequisite_RefD15_Math.csv"
            scoreCorteLeven = scoreCorteLeven_RefD15_Math
            scoreCorteLevenNorm = scoreCorteLevenNorm_RefD15_Math
            scoreCorteSimilar = scoreCorteSimilar_RefD15_Math
            scoreCorteLevenInvertido = scoreCorteLevenInvertido_RefD15_Math
            scoreCorteLevenNormInvertido = scoreCorteLevenNormInvertido_RefD15_Math
            scoreCorteSimilarInvertido = scoreCorteSimilarInvertido_RefD15_Math
        elif (nomeDataSet == "RefD15_CS"):
            caminhoSaida = './' + str(thresholdAvaliacao) + '/CS/' 
            nomePasta = 'CS'
            arquivoEntrada = "07-07-19-MLPrerequisite_RefD15_CS.csv"
            arquivoEntrada2 = "19-03-20-MLPrerequisite_RefD15_CS.csv"
            scoreCorteLeven = scoreCorteLeven_RefD15_CS
            scoreCorteLevenNorm = scoreCorteLevenNorm_RefD15_CS
            scoreCorteSimilar = scoreCorteSimilar_RefD15_CS     
            scoreCorteLevenInvertido = scoreCorteLevenInvertido_RefD15_CS
            scoreCorteLevenNormInvertido = scoreCorteLevenNormInvertido_RefD15_CS
            scoreCorteSimilarInvertido = scoreCorteSimilarInvertido_RefD15_CS          
        elif (nomeDataSet == "eaai17"):
            caminhoSaida = './' + str(thresholdAvaliacao) + '/EAAI17/'
            nomePasta = 'EAAI17'
            arquivoEntrada = "07-07-19-MLPrerequisite_eaai17.csv"
            arquivoEntrada2 = "19-03-20-MLPrerequisite_eaai17.csv"
            scoreCorteLeven = scoreCorteLeven_eaai17
            scoreCorteLevenNorm = scoreCorteLevenNorm_eaai17
            scoreCorteSimilar = scoreCorteSimilar_eaai17
            scoreCorteLevenInvertido = scoreCorteLevenInvertido_eaai17
            scoreCorteLevenNormInvertido = scoreCorteLevenNormInvertido_eaai17
            scoreCorteSimilarInvertido = scoreCorteSimilarInvertido_eaai17            

        now = datetime.now()
        print (now)
        listaMetodos = ['refDEqual','refDTFIDFNormal']
        listaMetodos = ['refDTFIDFCorteSimilar_'+str(scoreCorteSimilar),'refDSimilarCorteSimilar_'+str(scoreCorteSimilar),'refDLevenCorteLeven_'+str(scoreCorteLeven)]
        listaMetodos = ['refDSimilarCorteSimilar_'+str(scoreCorteSimilar),'refDLevenCorteLeven_'+str(scoreCorteLeven)]
        listaMetodos = ['refDLevenCorteLeven_'+str(scoreCorteLeven)]
        listaMetodos = ['refDEqual','refDTFIDFNormal','refDLevenPeso','refDTFIDF_Prop','refDSimilarPeso','refDTFIDFCorteLeven_'+str(scoreCorteLeven)]
        listaMetodos = ['refDLevenCorteLeven_'+str(scoreCorteLeven),'refDLevenNormCorteLevenNorm_'+str(scoreCorteLevenNorm)]
        #essa eu rodei mais cedo verde mais amarelo na planilha
        listaMetodos = ['refDEqual','refDTFIDFNormal','refDLevenPeso','refDLevenNormPeso','refDTFIDF_Prop','refDSimilarPeso','refDTFIDFCorteLeven_'+str(scoreCorteLeven),'refDTFIDFCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDTFIDFCorteSimilar_'+str(scoreCorteSimilar),'refDSimilarCorteSimilar_'+str(scoreCorteSimilar),'refDLevenCorteLeven_'+str(scoreCorteLeven),'refDLevenNormCorteLevenNorm_'+str(scoreCorteLevenNorm)]
        #essa sao as outras doze em azul na planilha
        listaMetodos = ['refDEqualCorteSimilar_'+str(scoreCorteSimilar),'refDLevenCorteSimilar_'+str(scoreCorteSimilar),'refDLevenNormCorteSimilar_'+str(scoreCorteSimilar),'refDTFIDF_PropCorteSimilar_'+str(scoreCorteSimilar),'refDEqualCorteLeven_'+str(scoreCorteLeven),'refDLevenNormCorteLeven_'+str(scoreCorteLeven),'refDSimilarCorteLeven_'+str(scoreCorteLeven),'refDTFIDF_PropCorteLeven_'+str(scoreCorteLeven),'refDEqualCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDLevenCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDSimilarCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDTFIDF_PropCorteLevenNorm_'+str(scoreCorteLevenNorm)]
        #essa sao as 12 em azul mais 3 em  amarelo na planilha
        listaMetodos = ['refDEqualCorteSimilar_'+str(scoreCorteSimilar),'refDLevenCorteSimilar_'+str(scoreCorteSimilar),'refDLevenNormCorteSimilar_'+str(scoreCorteSimilar),'refDTFIDF_PropCorteSimilar_'+str(scoreCorteSimilar),'refDEqualCorteLeven_'+str(scoreCorteLeven),'refDLevenNormCorteLeven_'+str(scoreCorteLeven),'refDSimilarCorteLeven_'+str(scoreCorteLeven),'refDTFIDF_PropCorteLeven_'+str(scoreCorteLeven),'refDEqualCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDLevenCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDSimilarCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDTFIDF_PropCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDSimilarCorteSimilar_'+str(scoreCorteSimilar),'refDLevenCorteLeven_'+str(scoreCorteLeven),'refDLevenNormCorteLevenNorm_'+str(scoreCorteLevenNorm)]

        #lista de invertidos
        
        listaMetodos = ['refDSimilarCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDTFIDF_PropCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDTFIDF_PropCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDTFIDF_PropCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido)]
        listaMetodos = ['refDEqualCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDEqualCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDEqualCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDTFIDFCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDTFIDFCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDTFIDFCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDLevenCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDLevenCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDLevenCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDLevenNormCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDLevenNormCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDLevenNormCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDSimilarCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDSimilarCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDSimilarCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDTFIDF_PropCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDTFIDF_PropCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDTFIDF_PropCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido)]

        #todos
        listaMetodos = ['refDEqual','refDTFIDFNormal','refDLevenPeso','refDLevenNormPeso','refDTFIDF_Prop','refDSimilarPeso','refDTFIDFCorteLeven_'+str(scoreCorteLeven),'refDTFIDFCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDTFIDFCorteSimilar_'+str(scoreCorteSimilar),'refDSimilarCorteSimilar_'+str(scoreCorteSimilar),'refDLevenCorteLeven_'+str(scoreCorteLeven),'refDLevenNormCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDEqualCorteSimilar_'+str(scoreCorteSimilar),'refDLevenCorteSimilar_'+str(scoreCorteSimilar),'refDLevenNormCorteSimilar_'+str(scoreCorteSimilar),'refDTFIDF_PropCorteSimilar_'+str(scoreCorteSimilar),'refDEqualCorteLeven_'+str(scoreCorteLeven),'refDLevenNormCorteLeven_'+str(scoreCorteLeven),'refDSimilarCorteLeven_'+str(scoreCorteLeven),'refDTFIDF_PropCorteLeven_'+str(scoreCorteLeven),'refDEqualCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDLevenCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDSimilarCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDTFIDF_PropCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDEqualCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDEqualCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDEqualCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDTFIDFCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDTFIDFCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDTFIDFCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDLevenCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDLevenCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDLevenCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDLevenNormCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDLevenNormCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDLevenNormCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDSimilarCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDSimilarCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDSimilarCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDTFIDF_PropCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDTFIDF_PropCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDTFIDF_PropCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido)]        
        
        #os ultimos 18
        listaMetodos = ['refDEqualCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDEqualCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDEqualCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDTFIDFCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDTFIDFCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDTFIDFCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDLevenCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDLevenCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDLevenCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDLevenNormCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDLevenNormCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDLevenNormCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDSimilarCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDSimilarCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDSimilarCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDTFIDF_PropCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDTFIDF_PropCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDTFIDF_PropCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido)]
        listaMetodos = ['refDTFIDFNormal','refDTFIDFCorteLeven_'+str(scoreCorteLeven)]
        listaMetodos = ['refDCossenoWikipediaAbstract']
        listaMetodos = ['refDEqual','refDTFIDFNormal','refDLevenPeso','refDLevenNormPeso','refDTFIDF_Prop','refDSimilarPeso','refDTFIDFCorteLeven_'+str(scoreCorteLeven),'refDTFIDFCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDTFIDFCorteSimilar_'+str(scoreCorteSimilar),'refDSimilarCorteSimilar_'+str(scoreCorteSimilar),'refDLevenCorteLeven_'+str(scoreCorteLeven),'refDLevenNormCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDEqualCorteSimilar_'+str(scoreCorteSimilar),'refDLevenCorteSimilar_'+str(scoreCorteSimilar),'refDLevenNormCorteSimilar_'+str(scoreCorteSimilar),'refDTFIDF_PropCorteSimilar_'+str(scoreCorteSimilar),'refDEqualCorteLeven_'+str(scoreCorteLeven),'refDLevenNormCorteLeven_'+str(scoreCorteLeven),'refDSimilarCorteLeven_'+str(scoreCorteLeven),'refDTFIDF_PropCorteLeven_'+str(scoreCorteLeven),'refDEqualCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDLevenCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDSimilarCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDTFIDF_PropCorteLevenNorm_'+str(scoreCorteLevenNorm),'refDEqualCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDEqualCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDEqualCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDTFIDFCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDTFIDFCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDTFIDFCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDLevenCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDLevenCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDLevenCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDLevenNormCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDLevenNormCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDLevenNormCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDSimilarCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDSimilarCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDSimilarCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido),'refDTFIDF_PropCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido),'refDTFIDF_PropCorteLevenInvertido_'+str(scoreCorteLevenInvertido),'refDTFIDF_PropCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido)]        
        
        now = datetime.now()
        print (now)
        for nomeMetodo in listaMetodos:
            listaId = []
            listaConceitoA = []
            listaConceitoB = []
            listaPreRequisito = []
            listaRefD = []
            listaResult = []
            listaabstractconceitoA=[]
            listaabstractconceitoB = []

            listaQtdeConceitosAntesCorteComumIndB_NeighA = []
            listaQtdeConceitosAntesCorteComumIndA_NeighB = []
            listaQtdeConceitosAntesCorteComum_NeighA = []
            listaQtdeConceitosAntesCorteComum_Neighb = []
            listaQtdeConceitosPosCorteComumIndB_NeighA = []
            listaQtdeConceitosPosCorteComumIndA_NeighB = []
            listaQtdeConceitosPosCorteComum_NeighA = []
            listaQtdeConceitosPosCorteComum_Neighb = []

            arquivoSaida = ""
            if nomeMetodo == 'refDEqual':
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_Equal.csv"
            elif nomeMetodo == 'refDTFIDFNormal':
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_TFIDFNormal.csv"
            elif nomeMetodo == 'refDLevenPeso':
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_refDLevenPeso.csv"
            elif nomeMetodo == 'refDLevenNormPeso':
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_refDLevenNormPeso.csv"                
            elif nomeMetodo == 'refDTFIDF_Prop':
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_TFIDF_Prop.csv"
            elif nomeMetodo == 'refDSimilarPeso':
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_SimilarPeso.csv"
            elif nomeMetodo == 'refDTFIDFCorteLeven_'+str(scoreCorteLeven):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_TFIDFCorteLeven_"+str(scoreCorteLeven)+".csv"
            elif nomeMetodo == 'refDTFIDFCorteLevenNorm_'+str(scoreCorteLevenNorm):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_CorteLevenNorm_"+str(scoreCorteLevenNorm)+".csv"                
            elif nomeMetodo == 'refDTFIDFCorteSimilar_'+str(scoreCorteSimilar):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_CorteSimilar_"+str(scoreCorteSimilar)+".csv"
            elif nomeMetodo == 'refDCossenoWikipediaAbstract':
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_CossenoWikipediaAbstract.csv"
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_CossenoWikipediaAbstract_CI.csv"
            elif nomeMetodo == 'refDSimilarCorteSimilar_'+str(scoreCorteSimilar):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_SimilarCorteSimilar"+str(scoreCorteSimilar)+".csv"            
            elif nomeMetodo == 'refDLevenCorteLeven_'+str(scoreCorteLeven):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_LevenCorteLeven"+str(scoreCorteLeven)+".csv"
            elif nomeMetodo == 'refDLevenNormCorteLevenNorm_'+str(scoreCorteLevenNorm):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_LevenNormCorteLevenNorm"+str(scoreCorteLevenNorm)+".csv"
            elif nomeMetodo == 'refDEqualCorteSimilar_'+str(scoreCorteSimilar):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_EqualCorteSimilar"+str(scoreCorteSimilar)+".csv"        
            elif nomeMetodo == 'refDLevenCorteSimilar_'+str(scoreCorteSimilar):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_LevenCorteSimilar"+str(scoreCorteSimilar)+".csv"
            elif nomeMetodo == 'refDLevenNormCorteSimilar_'+str(scoreCorteSimilar):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_LevenNormCorteSimilar"+str(scoreCorteSimilar)+".csv"
            elif nomeMetodo == 'refDTFIDF_PropCorteSimilar_'+str(scoreCorteSimilar):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_TFIDF_PropCorteSimilar"+str(scoreCorteSimilar)+".csv"
            elif nomeMetodo == 'refDEqualCorteLeven_'+str(scoreCorteLeven):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_EqualCorteLeven_"+str(scoreCorteLeven)+".csv"
            elif nomeMetodo == 'refDLevenNormCorteLeven_'+str(scoreCorteLeven):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_LevenNormCorteLeven_"+str(scoreCorteLeven)+".csv"
            elif nomeMetodo == 'refDSimilarCorteLeven_'+str(scoreCorteLeven):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_SimilarCorteLeven_"+str(scoreCorteLeven)+".csv"
            elif nomeMetodo == 'refDTFIDF_PropCorteLeven_'+str(scoreCorteLeven):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_TFIDF_PropCorteLeven_"+str(scoreCorteLeven)+".csv"
            elif nomeMetodo == 'refDEqualCorteLevenNorm_'+str(scoreCorteLevenNorm):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_EqualCorteLevenNorm_"+str(scoreCorteLevenNorm)+".csv"                
            elif nomeMetodo == 'refDLevenCorteLevenNorm_'+str(scoreCorteLevenNorm):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_LevenCorteLevenNorm_"+str(scoreCorteLevenNorm)+".csv"
            elif nomeMetodo == 'refDSimilarCorteLevenNorm_'+str(scoreCorteLevenNorm):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_SimilarCorteLevenNorm_"+str(scoreCorteLevenNorm)+".csv"
            elif nomeMetodo == 'refDTFIDF_PropCorteLevenNorm_'+str(scoreCorteLevenNorm):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"_TFIDF_PropCorteLevenNorm_"+str(scoreCorteLevenNorm)+".csv"

            elif nomeMetodo == 'refDEqualCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"EqualCorteSimilarInvertido"+str(scoreCorteSimilarInvertido)+".csv"
            elif nomeMetodo == 'refDEqualCorteLevenInvertido_'+str(scoreCorteLevenInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"EqualCorteLevenInvertido_"+str(scoreCorteLevenInvertido)+".csv"
            elif nomeMetodo == 'refDEqualCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"EqualCorteLevenNormInvertido_"+str(scoreCorteLevenNormInvertido)+".csv"
            elif nomeMetodo == 'refDTFIDFCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"TFIDFCorteSimilarInvertido_"+str(scoreCorteSimilarInvertido)+".csv"
            elif nomeMetodo == 'refDTFIDFCorteLevenInvertido_'+str(scoreCorteLevenInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"TFIDFCorteLevenInvertido_"+str(scoreCorteLevenInvertido)+".csv"
            elif nomeMetodo == 'refDTFIDFCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"TFIDFCorteLevenNormInvertido_"+str(scoreCorteLevenNormInvertido)+".csv"
            elif nomeMetodo == 'refDLevenCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"LevenCorteSimilarInvertido"+str(scoreCorteSimilarInvertido)+".csv"
            elif nomeMetodo == 'refDLevenCorteLevenInvertido_'+str(scoreCorteLevenInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"LevenCorteLevenInvertido_"+str(scoreCorteLevenInvertido)+".csv"
            elif nomeMetodo == 'refDLevenCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"LevenCorteLevenNormInvertido_"+str(scoreCorteLevenNormInvertido)+".csv"
            elif nomeMetodo == 'refDLevenNormCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"LevenNormCorteSimilarInvertido_"+str(scoreCorteSimilarInvertido)+".csv"
            elif nomeMetodo == 'refDLevenNormCorteLevenInvertido_'+str(scoreCorteLevenInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"LevenNormCorteLevenInvertido_"+str(scoreCorteLevenInvertido)+".csv"
            elif nomeMetodo == 'refDLevenNormCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"LevenNormCorteLevenNormInvertido_"+str(scoreCorteLevenNormInvertido)+".csv"
            elif nomeMetodo == 'refDSimilarCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"SimilarCorteSimilarInvertido_"+str(scoreCorteSimilarInvertido)+".csv"
            elif nomeMetodo == 'refDSimilarCorteLevenInvertido_'+str(scoreCorteLevenInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"SimilarCorteLevenInvertido_"+str(scoreCorteLevenInvertido)+".csv"
            elif nomeMetodo == 'refDSimilarCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"SimilarCorteLevenNormInvertido_"+str(scoreCorteLevenNormInvertido)+".csv"
            elif nomeMetodo == 'refDTFIDF_PropCorteSimilarInvertido_'+str(scoreCorteSimilarInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"TFIDF_PropCorteSimilarInvertido_"+str(scoreCorteSimilarInvertido)+".csv"
            elif nomeMetodo == 'refDTFIDF_PropCorteLevenInvertido_'+str(scoreCorteLevenInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"TFIDF_PropCorteLevenInvertido_"+str(scoreCorteLevenInvertido)+".csv"
            elif nomeMetodo == 'refDTFIDF_PropCorteLevenNormInvertido_'+str(scoreCorteLevenNormInvertido):
                arquivoSaida = "MLPrerequisite_"+nomeDataSet+"TFIDF_PropCorteLevenNormInvertido"+str(scoreCorteLevenNormInvertido)+".csv"

            else:
                raise ValueError('RefD nao definido')
            if nomeMetodo == 'refDCossenoWikipediaAbstract':
                calculaRefDGeral(arquivoEntrada2,arquivoSaida,nomeMetodo)
            else:
                calculaRefDGeral(arquivoEntrada,arquivoSaida,nomeMetodo)
        now = datetime.now()
        print (now)
except Exception as e:
    print (e)
