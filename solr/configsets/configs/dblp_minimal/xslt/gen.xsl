<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match="/">
    <add>
      <xsl:apply-templates/>
    </add>
  </xsl:template>
  <xsl:template match="article">
    <doc>
      <field name="pub_type">article</field>
      <field name="key">
        <xsl:value-of select="@key"/>
      </field>
      <field name="cdate">
        <xsl:value-of select="@cdate"/>
      </field>
      <field name="rating">
        <xsl:value-of select="@rating"/>
      </field>
      <field name="reviewid">
        <xsl:value-of select="@reviewid"/>
      </field>
      <field name="publtype">
        <xsl:value-of select="@publtype"/>
      </field>
      <field name="mdate">
        <xsl:value-of select="@mdate"/>
      </field>
      <xsl:apply-templates/>
    </doc>
  </xsl:template>
  <xsl:template match="inproceedings">
    <doc>
      <field name="pub_type">inproceedings</field>
      <field name="key">
        <xsl:value-of select="@key"/>
      </field>
      <field name="cdate">
        <xsl:value-of select="@cdate"/>
      </field>
      <field name="publtype">
        <xsl:value-of select="@publtype"/>
      </field>
      <field name="mdate">
        <xsl:value-of select="@mdate"/>
      </field>
      <xsl:apply-templates/>
    </doc>
  </xsl:template>
  <xsl:template match="proceedings">
    <doc>
      <field name="pub_type">proceedings</field>
      <field name="key">
        <xsl:value-of select="@key"/>
      </field>
      <field name="cdate">
        <xsl:value-of select="@cdate"/>
      </field>
      <field name="publtype">
        <xsl:value-of select="@publtype"/>
      </field>
      <field name="mdate">
        <xsl:value-of select="@mdate"/>
      </field>
      <xsl:apply-templates/>
    </doc>
  </xsl:template>
  <xsl:template match="book">
    <doc>
      <field name="pub_type">book</field>
      <field name="key">
        <xsl:value-of select="@key"/>
      </field>
      <field name="cdate">
        <xsl:value-of select="@cdate"/>
      </field>
      <field name="publtype">
        <xsl:value-of select="@publtype"/>
      </field>
      <field name="mdate">
        <xsl:value-of select="@mdate"/>
      </field>
      <xsl:apply-templates/>
    </doc>
  </xsl:template>
  <xsl:template match="incollection">
    <doc>
      <field name="pub_type">incollection</field>
      <field name="key">
        <xsl:value-of select="@key"/>
      </field>
      <field name="cdate">
        <xsl:value-of select="@cdate"/>
      </field>
      <field name="publtype">
        <xsl:value-of select="@publtype"/>
      </field>
      <field name="mdate">
        <xsl:value-of select="@mdate"/>
      </field>
      <xsl:apply-templates/>
    </doc>
  </xsl:template>
  <xsl:template match="phdthesis">
    <doc>
      <field name="pub_type">phdthesis</field>
      <field name="key">
        <xsl:value-of select="@key"/>
      </field>
      <field name="cdate">
        <xsl:value-of select="@cdate"/>
      </field>
      <field name="publtype">
        <xsl:value-of select="@publtype"/>
      </field>
      <field name="mdate">
        <xsl:value-of select="@mdate"/>
      </field>
      <xsl:apply-templates/>
    </doc>
  </xsl:template>
  <xsl:template match="mastersthesis">
    <doc>
      <field name="pub_type">mastersthesis</field>
      <field name="key">
        <xsl:value-of select="@key"/>
      </field>
      <field name="cdate">
        <xsl:value-of select="@cdate"/>
      </field>
      <field name="publtype">
        <xsl:value-of select="@publtype"/>
      </field>
      <field name="mdate">
        <xsl:value-of select="@mdate"/>
      </field>
      <xsl:apply-templates/>
    </doc>
  </xsl:template>
  <xsl:template match="www">
    <doc>
      <field name="pub_type">www</field>
      <field name="key">
        <xsl:value-of select="@key"/>
      </field>
      <field name="cdate">
        <xsl:value-of select="@cdate"/>
      </field>
      <field name="publtype">
        <xsl:value-of select="@publtype"/>
      </field>
      <field name="mdate">
        <xsl:value-of select="@mdate"/>
      </field>
      <xsl:apply-templates/>
    </doc>
  </xsl:template>
  <xsl:template match="person">
    <doc>
      <field name="pub_type">person</field>
      <field name="key">
        <xsl:value-of select="@key"/>
      </field>
      <field name="cdate">
        <xsl:value-of select="@cdate"/>
      </field>
      <field name="mdate">
        <xsl:value-of select="@mdate"/>
      </field>
      <xsl:apply-templates/>
    </doc>
  </xsl:template>
  <xsl:template match="data">
    <doc>
      <field name="pub_type">data</field>
      <field name="key">
        <xsl:value-of select="@key"/>
      </field>
      <field name="cdate">
        <xsl:value-of select="@cdate"/>
      </field>
      <field name="publtype">
        <xsl:value-of select="@publtype"/>
      </field>
      <field name="mdate">
        <xsl:value-of select="@mdate"/>
      </field>
      <xsl:apply-templates/>
    </doc>
  </xsl:template>
  <xsl:template match="author">
    <field name="author">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="editor">
    <field name="editor">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="title">
    <field name="title">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="booktitle">
    <field name="booktitle">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="pages">
    <field name="pages">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="year">
    <field name="year">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="address">
    <field name="address">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="journal">
    <field name="journal">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="volume">
    <field name="volume">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="number">
    <field name="number">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="month">
    <field name="month">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="url">
    <field name="url">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="ee">
    <field name="ee">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="cdrom">
    <field name="cdrom">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="cite">
    <field name="cite">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="publisher">
    <field name="publisher">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="note">
    <field name="note">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="crossref">
    <field name="crossref">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="isbn">
    <field name="isbn">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="series">
    <field name="series">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="school">
    <field name="school">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="chapter">
    <field name="chapter">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
  <xsl:template match="publnr">
    <field name="publnr">
      <xsl:value-of select="."/>
    </field>
  </xsl:template>
</xsl:stylesheet>
