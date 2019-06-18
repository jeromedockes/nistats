<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform version="1.0"
               xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
               xmlns:svg="http://www.w3.org/2000/svg"
               xmlns:xhtml="http://www.w3.org/1999/xhtml"
               xmlns="http://www.w3.org/1999/xhtml"
               xmlns:nistats="https://nistats.github.io" >
  <xsl:output method="xhtml" encoding="UTF-8" />
  <xsl:strip-space elements="*"/>

  <xsl:template match="text()" />

  <xsl:template match="/">
    <html lang="en">
      <head>
        <title><xsl:value-of select="/nistats:report/nistats:title/text()"/></title>
        <meta charset="UTF-8"/>
        <style>
          table {
            border-collapse: collapse;
          }

          table, th, td {
            border: 1px solid black;
          }
        </style>
      </head>
      <body>
        <div>
          <xsl:apply-templates/>
        </div>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="nistats:title">
    <h1><xsl:value-of select="text()"/></h1>
  </xsl:template>

  <xsl:template match="nistats:model_parameters">
    <div>
      <h2>model parameters</h2>
      <p>
      <xsl:for-each select="nistats:model_parameter">
        <span>
          <xsl:attribute name="title">description: "<xsl:value-of
            select="nistats:parameter_description"/>"</xsl:attribute>
          <b><xsl:value-of select="nistats:parameter_name"/>: </b><xsl:value-of
          select="nistats:parameter_value"/>
        </span>
        <br/>
      </xsl:for-each>
      </p>
    </div>
  </xsl:template>

  <xsl:template match="nistats:contrast">
    <hr/>
    <div>
      <h2>Contrast: <xsl:value-of select="nistats:contrast_name"/></h2>
      <p>Statistic type: <xsl:value-of select="nistats:statistic_type"/></p>
      <xsl:apply-templates />
    </div>
  </xsl:template>

  <xsl:template match="nistats:clusters_table">
    <h3>Peak activations</h3>
    <xsl:apply-templates select="table" mode="pandas-table" />
  </xsl:template>

  <xsl:template match="svg:svg">
    <xsl:copy-of select="."/>
  </xsl:template>

  <xsl:template match="nistats:design_matrices">
    <hr/>
    <div>
      <h2>Design matrices</h2>
      <xsl:for-each select="nistats:design_matrix">
        <h3>Run <xsl:value-of select="position()"/></h3>
        <xsl:apply-templates select="svg:svg"/>
        <!-- <xsl:apply-templates select="table" mode="pandas-table"/> -->
      </xsl:for-each>
    </div>
  </xsl:template>

  <xsl:template match="*" mode="pandas-table">
    <xsl:element name="{local-name()}" namespace="http://www.w3.org/1999/xhtml">
      <xsl:apply-templates select="@*|node()" mode="pandas-table"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="@*" mode="pandas-table">
    <xsl:attribute name="{name()}"><xsl:value-of select="."/></xsl:attribute>
  </xsl:template>

  <xsl:template match="@border" mode="pandas-table"/>

</xsl:transform>
