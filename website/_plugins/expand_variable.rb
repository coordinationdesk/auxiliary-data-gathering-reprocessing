# file: _plugins/expand_variable.rb
# Telespazio S.p.A.
# Added 2024-07-08
# Example taken from http://acegik.net/blog/ruby/jekyll/plugins/howto-nest-liquid-template-variables-inside-yaml-front-matter-block.html


module Jekyll
	module ExpandNestedVariableFilter
		def expand_variable(input)
			Liquid::Template.parse(input).render(@context)
		end
	end
end

Liquid::Template.register_filter(Jekyll::ExpandNestedVariableFilter)
