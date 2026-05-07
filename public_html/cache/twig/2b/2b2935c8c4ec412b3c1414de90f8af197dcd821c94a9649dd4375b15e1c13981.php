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

/* partials/blog_item.html.twig */
class __TwigTemplate_6c8d8c2c1c6fbd4e4014d3d87b2e37fe33a02c7fd1ab602849bad7c05067da99 extends \Twig\Template
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
        echo "<div class=\"product-card\">
    <a href=\"";
        // line 2
        echo twig_escape_filter($this->env, $this->getAttribute(($context["page"] ?? null), "url", []), "html", null, true);
        echo "\">
        <div class=\"product-image-wrap\">
            ";
        // line 4
        if (twig_first($this->env, $this->getAttribute($this->getAttribute(($context["page"] ?? null), "media", []), "images", []))) {
            // line 5
            echo "                ";
            echo $this->getAttribute(twig_first($this->env, $this->getAttribute($this->getAttribute(($context["page"] ?? null), "media", []), "images", [])), "html", []);
            echo "
            ";
        }
        // line 7
        echo "        </div>
        <h4>";
        // line 8
        echo twig_escape_filter($this->env, $this->getAttribute(($context["page"] ?? null), "title", []), "html", null, true);
        echo "</h4>
    </a>
</div>";
    }

    public function getTemplateName()
    {
        return "partials/blog_item.html.twig";
    }

    public function isTraitable()
    {
        return false;
    }

    public function getDebugInfo()
    {
        return array (  49 => 8,  46 => 7,  40 => 5,  38 => 4,  33 => 2,  30 => 1,);
    }

    /** @deprecated since 1.27 (to be removed in 2.0). Use getSourceContext() instead */
    public function getSource()
    {
        @trigger_error('The '.__METHOD__.' method is deprecated since version 1.27 and will be removed in 2.0. Use getSourceContext() instead.', E_USER_DEPRECATED);

        return $this->getSourceContext()->getCode();
    }

    public function getSourceContext()
    {
        return new Source("<div class=\"product-card\">
    <a href=\"{{ page.url }}\">
        <div class=\"product-image-wrap\">
            {% if page.media.images|first %}
                {{ page.media.images|first.html|raw }}
            {% endif %}
        </div>
        <h4>{{ page.title }}</h4>
    </a>
</div>", "partials/blog_item.html.twig", "/home/1311902.cloudwaysapps.com/apbngamsdv/public_html/user/themes/deliver/templates/partials/blog_item.html.twig");
    }
}
