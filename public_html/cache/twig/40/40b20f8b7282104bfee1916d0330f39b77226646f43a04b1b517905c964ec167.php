<?php

use Twig\Environment;
use Twig\Error\LoaderError;
use Twig\Error\RuntimeError;
use Twig\Markup;
use Twig\Sandbox\SecurityError;
use Twig\Sandbox\SecurityNotAllowedTagError;
use Twig\Sandbox\SecurityNotAllowedFilterError;
use Twig\Sandbox\SecurityNotAllowedFunctionError;
use Twig\Source;
use Twig\Template;

/* blog.html.twig */
class __TwigTemplate_c4bf5ee74d83837e4202264670d3718c3141a392c28003ee41715741aac59fa6 extends \Twig\Template
{
    public function __construct(Environment $env)
    {
        parent::__construct($env);

        $this->parent = false;

        $this->blocks = [
        ];
    }

    protected function doDisplay(array $context, array $blocks = [])
    {
        // line 1
        $this->loadTemplate("blog.html.twig", "blog.html.twig", 1, "1338884364")->display($context);
    }

    public function getTemplateName()
    {
        return "blog.html.twig";
    }

    public function getDebugInfo()
    {
        return array (  30 => 1,);
    }

    /** @deprecated since 1.27 (to be removed in 2.0). Use getSourceContext() instead */
    public function getSource()
    {
        @trigger_error('The '.__METHOD__.' method is deprecated since version 1.27 and will be removed in 2.0. Use getSourceContext() instead.', E_USER_DEPRECATED);

        return $this->getSourceContext()->getCode();
    }

    public function getSourceContext()
    {
        return new Source("{% embed 'partials/base.html.twig' %}

{% set collection = page.collection() %}

{% block content %}
{% set blog_image = page.media.images|first %}

{% if blog_image %}
<div class=\"flush-top blog-header blog-header-image\" style=\"background: {{ page.header.bg_color }} url({{ blog_image.url }}) no-repeat right;\">
{% else %}
<div class=\"blog-header\">
{% endif %}
    {{ page.content|raw }}
</div>

<div class=\"content-wrapper\">
    <div class=\"product-grid\">
        {% for child in collection %}
            {% include 'partials/blog_item.html.twig' with {'page':child} %}
        {% endfor %}
    </div>
</div>
{% endblock %}

{% endembed %}", "blog.html.twig", "/home/1311902.cloudwaysapps.com/apbngamsdv/public_html/user/themes/deliver/templates/blog.html.twig");
    }
}


/* blog.html.twig */
class __TwigTemplate_c4bf5ee74d83837e4202264670d3718c3141a392c28003ee41715741aac59fa6___1338884364 extends \Twig\Template
{
    public function __construct(Environment $env)
    {
        parent::__construct($env);

        $this->blocks = [
            'content' => [$this, 'block_content'],
        ];
    }

    protected function doGetParent(array $context)
    {
        return "partials/base.html.twig";
    }

    protected function doDisplay(array $context, array $blocks = [])
    {
        // line 3
        $context["collection"] = $this->getAttribute(($context["page"] ?? null), "collection", [], "method");
        // line 1
        $this->parent = $this->loadTemplate("partials/base.html.twig", "blog.html.twig", 1);
        $this->parent->display($context, array_merge($this->blocks, $blocks));
    }

    // line 5
    public function block_content($context, array $blocks = [])
    {
        // line 6
        $context["blog_image"] = twig_first($this->env, $this->getAttribute($this->getAttribute(($context["page"] ?? null), "media", []), "images", []));
        // line 7
        echo "
";
        // line 8
        if (($context["blog_image"] ?? null)) {
            // line 9
            echo "<div class=\"flush-top blog-header blog-header-image\" style=\"background: ";
            echo twig_escape_filter($this->env, $this->getAttribute($this->getAttribute(($context["page"] ?? null), "header", []), "bg_color", []), "html", null, true);
            echo " url(";
            echo twig_escape_filter($this->env, $this->getAttribute(($context["blog_image"] ?? null), "url", []), "html", null, true);
            echo ") no-repeat right;\">
";
        } else {
            // line 11
            echo "<div class=\"blog-header\">
";
        }
        // line 13
        echo "    ";
        echo $this->getAttribute(($context["page"] ?? null), "content", []);
        echo "
</div>

<div class=\"content-wrapper\">
    <div class=\"product-grid\">
        ";
        // line 18
        $context['_parent'] = $context;
        $context['_seq'] = twig_ensure_traversable(($context["collection"] ?? null));
        $context['loop'] = [
          'parent' => $context['_parent'],
          'index0' => 0,
          'index'  => 1,
          'first'  => true,
        ];
        if (is_array($context['_seq']) || (is_object($context['_seq']) && $context['_seq'] instanceof \Countable)) {
            $length = count($context['_seq']);
            $context['loop']['revindex0'] = $length - 1;
            $context['loop']['revindex'] = $length;
            $context['loop']['length'] = $length;
            $context['loop']['last'] = 1 === $length;
        }
        foreach ($context['_seq'] as $context["_key"] => $context["child"]) {
            // line 19
            echo "            ";
            $this->loadTemplate("partials/blog_item.html.twig", "blog.html.twig", 19)->display(twig_array_merge($context, ["page" => $context["child"]]));
            // line 20
            echo "        ";
            ++$context['loop']['index0'];
            ++$context['loop']['index'];
            $context['loop']['first'] = false;
            if (isset($context['loop']['length'])) {
                --$context['loop']['revindex0'];
                --$context['loop']['revindex'];
                $context['loop']['last'] = 0 === $context['loop']['revindex0'];
            }
        }
        $_parent = $context['_parent'];
        unset($context['_seq'], $context['_iterated'], $context['_key'], $context['child'], $context['_parent'], $context['loop']);
        $context = array_intersect_key($context, $_parent) + $_parent;
        // line 21
        echo "    </div>
</div>
";
    }

    public function getTemplateName()
    {
        return "blog.html.twig";
    }

    public function isTraitable()
    {
        return false;
    }

    public function getDebugInfo()
    {
        return array (  174 => 21,  160 => 20,  157 => 19,  140 => 18,  131 => 13,  127 => 11,  119 => 9,  117 => 8,  114 => 7,  112 => 6,  109 => 5,  104 => 1,  102 => 3,  30 => 1,);
    }

    /** @deprecated since 1.27 (to be removed in 2.0). Use getSourceContext() instead */
    public function getSource()
    {
        @trigger_error('The '.__METHOD__.' method is deprecated since version 1.27 and will be removed in 2.0. Use getSourceContext() instead.', E_USER_DEPRECATED);

        return $this->getSourceContext()->getCode();
    }

    public function getSourceContext()
    {
        return new Source("{% embed 'partials/base.html.twig' %}

{% set collection = page.collection() %}

{% block content %}
{% set blog_image = page.media.images|first %}

{% if blog_image %}
<div class=\"flush-top blog-header blog-header-image\" style=\"background: {{ page.header.bg_color }} url({{ blog_image.url }}) no-repeat right;\">
{% else %}
<div class=\"blog-header\">
{% endif %}
    {{ page.content|raw }}
</div>

<div class=\"content-wrapper\">
    <div class=\"product-grid\">
        {% for child in collection %}
            {% include 'partials/blog_item.html.twig' with {'page':child} %}
        {% endfor %}
    </div>
</div>
{% endblock %}

{% endembed %}", "blog.html.twig", "/home/1311902.cloudwaysapps.com/apbngamsdv/public_html/user/themes/deliver/templates/blog.html.twig");
    }
}
